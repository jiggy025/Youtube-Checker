import os
import pickle
import time
import smtplib
import json
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ---------------- CONFIG ----------------
# Multiple giveaway videos to monitor (add more video IDs as needed)
VIDEO_IDS = [
    "k6ytzTGrvsk",  # Example giveaway video 1
    # Add more video IDs here as you comment on them
]

# Your YouTube channel IDs (your commenting automation channels)
YOUR_CHANNEL_IDS = [
    "UCc-ArbufTRA1TbfjXbBo6FQ",
    "UCxd6dwA_r_0-wVCi1FaiBIQ", 
    "UChfZ-3fb-DRPQEKjfotjJ_g",
    "UCGCPVQMEQJcs32RihuQJ4SQ",
    "UCF6wJFc2nZfEMfE0ENher8g",
    "UCr5k1Gqi95vsacGeeueaW2g",
    "UC8MuPdeBsj7FxMzAPyvkECQ",
    "UCi7bT2yZaqvA7syc8ellssA",
    "UCvB-kvimlxevwLbL_rQbp6w",
    "UCgkPoAZ1FzI85tQwTasI-hw",
    "UCImtKijLmVUsa_m6IqjXbKQ",
    "UCpvifJpTz3T4MecN-JUk1Pw",
    "UCz7vqkKyjag4fjutHjdDLrg",
    "UCgrPsCvLhsnK8fSeftjsfLw",
    "UCQGeEsdA-aK1RP7YRopHsEQ",
    "UCgKOtboYq_1qVfEUQ8qjixA",
    "UCdhfe2CCUQX4QPQYFD4_FlQ",
    "UCSUXjXKIvVM95m0RsB5hEzQ",
    "UCZ26gY-_irWFBNXTA2_5eTw",
    "UC6DDQQbL-Ye9GMeo3MMvAyA",
    # Add more channel IDs as you provide them
]

# Uploader channel IDs to watch for (the giveaway hosts)
UPLOADER_CHANNEL_IDS = [
    "UCbR7j6mcpOxPGS1sm_1AoOQ",  # Replace with actual uploader channel ID
    # Add more uploader channel IDs if monitoring multiple giveaway hosts
]

EMAIL_TO_NOTIFY = os.getenv("EMAIL_ADDRESS")  # your Gmail
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")  # Gmail App Password from environment
CHECK_INTERVAL = 60   # 1 minute

# State tracking for seen replies (prevents duplicate notifications)
SEEN_REPLIES_FILE = "seen_replies.json"
# ----------------------------------------

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def load_seen_replies():
    """Load previously seen reply IDs to prevent duplicate notifications"""
    try:
        if os.path.exists(SEEN_REPLIES_FILE):
            with open(SEEN_REPLIES_FILE, 'r') as f:
                return set(json.load(f))
        return set()
    except Exception as e:
        print(f"⚠️  Error loading seen replies: {e}")
        return set()

def save_seen_replies(seen_replies):
    """Save seen reply IDs to prevent duplicate notifications"""
    try:
        with open(SEEN_REPLIES_FILE, 'w') as f:
            json.dump(list(seen_replies), f)
    except Exception as e:
        print(f"⚠️  Error saving seen replies: {e}")

def get_all_replies_for_comment(youtube, comment_id):
    """Get ALL replies for a specific comment using pagination"""
    all_replies = []
    next_page_token = None
    
    while True:
        try:
            request_params = {
                'part': 'snippet',
                'parentId': comment_id,
                'maxResults': 100
            }
            if next_page_token:
                request_params['pageToken'] = next_page_token
                
            results = youtube.comments().list(**request_params).execute()
            all_replies.extend(results.get('items', []))
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
                
        except Exception as e:
            print(f"⚠️  Error getting replies for comment {comment_id}: {e}")
            break
            
    return all_replies

def get_youtube_service():
    """Authenticate and return YouTube API client"""
    creds = None
    
    # Load existing credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    
    # Check if credentials exist and are valid
    if not creds:
        print("❌ No authentication token found!")
        print("\n🔐 To set up authentication:")
        print("1. Download auth_bootstrap.py and client_secret.json to your local machine")
        print("2. Run: python auth_bootstrap.py")
        print("3. Upload the generated token.pickle file to this project")
        print("4. Restart this script")
        raise SystemExit("Authentication required")
    
    # Refresh expired credentials
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired authentication token...")
            creds.refresh(Request())
            # Save refreshed credentials
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
            print("✅ Token refreshed successfully")
        else:
            print("❌ Authentication token is invalid and cannot be refreshed!")
            print("Please run auth_bootstrap.py locally to generate a new token.")
            raise SystemExit("Token refresh failed")
    
    return build("youtube", "v3", credentials=creds)

def check_replies_on_video(youtube, video_id, seen_replies):
    """Check a specific video for uploader replies to any of your channels with full pagination"""
    new_replies = []
    next_page_token = None
    
    try:
        print(f"    📄 Scanning comments on video {video_id}...")
        
        # Get ALL comment threads with pagination
        while True:
            request_params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': 100,
                'order': 'time'  # Get newest first
            }
            if next_page_token:
                request_params['pageToken'] = next_page_token
                
            results = youtube.commentThreads().list(**request_params).execute()
            
            for item in results.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]
                top_comment_id = top_comment["id"]
                top_comment_author = top_comment["snippet"].get("authorChannelId", {}).get("value", "")
                
                # Check if the top-level comment is from one of your channels
                if top_comment_author in YOUR_CHANNEL_IDS:
                    print(f"    👤 Found your comment from channel {top_comment_author}")
                    
                    # Get ALL replies for this comment using dedicated API call
                    all_replies = get_all_replies_for_comment(youtube, top_comment_id)
                    
                    for reply in all_replies:
                        reply_id = reply["id"]
                        reply_author = reply["snippet"].get("authorChannelId", {}).get("value", "")
                        
                        # Skip if we've already seen this reply
                        if reply_id in seen_replies:
                            continue
                            
                        # Check if uploader replied to your comment
                        if reply_author in UPLOADER_CHANNEL_IDS:
                            new_reply = {
                                "reply_id": reply_id,
                                "video_id": video_id,
                                "your_channel": top_comment_author,
                                "uploader_channel": reply_author,
                                "reply_text": reply["snippet"]["textDisplay"],
                                "original_comment": top_comment["snippet"]["textDisplay"]
                            }
                            new_replies.append(new_reply)
                            seen_replies.add(reply_id)
                            print(f"    🎉 NEW UPLOADER REPLY FOUND!")
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
                
        return new_replies
        
    except Exception as e:
        print(f"⚠️  Error checking video {video_id}: {e}")
        return []

def check_all_videos(youtube, seen_replies):
    """Check all configured videos for uploader replies"""
    all_new_replies = []
    
    for video_id in VIDEO_IDS:
        print(f"🔍 Checking video: {video_id}")
        new_replies = check_replies_on_video(youtube, video_id, seen_replies)
        all_new_replies.extend(new_replies)
    
    return all_new_replies

def send_email(reply_info):
    """Send detailed email notification about uploader reply"""
    if not EMAIL_APP_PASSWORD:
        print("❌ Email password not configured!")
        print("Please set EMAIL_APP_PASSWORD environment variable.")
        return False
        
    try:
        # Create detailed email message
        email_body = f"""
🎉 GIVEAWAY UPLOADER REPLIED! 🎉

📺 Video: https://youtube.com/watch?v={reply_info['video_id']}
👤 Your Channel: {reply_info['your_channel']}
🎯 Uploader Channel: {reply_info['uploader_channel']}

💬 Your Original Comment:
"{reply_info['original_comment']}"

✨ Uploader's Reply:
"{reply_info['reply_text']}"

🔗 Direct link: https://youtube.com/watch?v={reply_info['video_id']}

Good luck with the giveaway! 🍀
        """
        
        msg = MIMEText(email_body)
        msg["Subject"] = f"🚨 Giveaway Reply Detected - {reply_info['video_id']}"
        msg["From"] = EMAIL_TO_NOTIFY
        msg["To"] = EMAIL_TO_NOTIFY

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_TO_NOTIFY, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_TO_NOTIFY, EMAIL_TO_NOTIFY, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Multi-Channel YouTube Giveaway Monitor Starting...")
    print(f"📺 Monitoring {len(VIDEO_IDS)} videos: {', '.join(VIDEO_IDS)}")
    print(f"👤 Watching for your channels: {', '.join(YOUR_CHANNEL_IDS)}")
    print(f"🎯 Watching for uploader channels: {', '.join(UPLOADER_CHANNEL_IDS)}")
    print(f"✉️  Will notify: {EMAIL_TO_NOTIFY}")
    print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print("=" * 60)
    
    # Load previously seen replies
    seen_replies = load_seen_replies()
    print(f"📋 Loaded {len(seen_replies)} previously seen replies")
    
    youtube = get_youtube_service()
    print("🔗 YouTube API connection established!")
    print()
    
    while True:
        print(f"🔍 Starting check cycle at {time.strftime('%H:%M:%S')}")
        new_replies = check_all_videos(youtube, seen_replies)
        
        if new_replies:
            print(f"🎉 FOUND {len(new_replies)} NEW UPLOADER REPLIES!")
            
            # Send email for each new reply
            for reply in new_replies:
                print(f"📺 Video: {reply['video_id']}")
                print(f"👤 Your Channel: {reply['your_channel']}")
                print(f"💬 Reply: {reply['reply_text']}")
                
                if send_email(reply):
                    print("✅ Email notification sent successfully!")
                else:
                    print("⚠️  Reply detected but email notification failed.")
                print("-" * 40)
            
            # Save updated seen replies
            save_seen_replies(seen_replies)
            print("💾 Saved updated reply tracking")
            
        else:
            print("❌ No new replies found across all videos")
            print(f"⏰ Next check in {CHECK_INTERVAL} seconds...")
            print()
        
        time.sleep(CHECK_INTERVAL)
