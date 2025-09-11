# Overview

This is a YouTube giveaway monitoring system that automatically tracks responses from contest hosts to user comments. The application monitors multiple YouTube videos for replies from specific uploader channels and sends email notifications when responses are detected. It's designed to help users stay informed about potential giveaway wins or important communications from YouTube content creators.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure

The system follows a simple polling-based architecture with three main components:

**Authentication Layer**: Uses Google OAuth 2.0 flow with local credential storage via pickle files. The `auth_bootstrap.py` script handles initial authentication setup for local development, while the main application loads stored credentials from `token.pickle`.

**YouTube API Integration**: Leverages Google's YouTube Data API v3 to fetch comment threads and replies. The system polls comment data at configurable intervals (currently 1 minute) to detect new responses from monitored channels.

**Notification System**: Implements SMTP-based email notifications using Gmail's service. Sends alerts when replies from target uploaders are detected on monitored videos.

## Data Storage

**State Management**: Uses a simple JSON file (`seen_replies.json`) to track already-processed replies and prevent duplicate notifications. This lightweight approach avoids the need for a traditional database.

**Configuration Storage**: All configuration is handled through environment variables and hardcoded constants, making the system easy to deploy and modify.

## Monitoring Logic

The application implements a multi-video, multi-channel monitoring system:
- Tracks multiple giveaway videos simultaneously via `VIDEO_IDS` array
- Monitors responses from specific uploader channels via `UPLOADER_CHANNEL_IDS`
- Filters for replies to comments from user's own channels via `YOUR_CHANNEL_IDS`

## Error Handling and Reliability

The system includes credential refresh mechanisms for expired tokens and basic error handling for API failures. The polling-based approach provides resilience against temporary service interruptions.

# External Dependencies

## Google Services
- **YouTube Data API v3**: Primary integration for accessing video comments and replies
- **Google OAuth 2.0**: Authentication mechanism for YouTube API access
- **Google Client Libraries**: `googleapiclient.discovery`, `google_auth_oauthlib.flow`, `google.auth.transport.requests`

## Email Services
- **Gmail SMTP**: Email notification delivery using app-specific passwords
- **Python SMTP Library**: Built-in email sending capabilities

## Third-Party Libraries
- **Python Standard Libraries**: `pickle`, `json`, `time`, `smtplib`, `os` for core functionality
- **Email MIME**: `email.mime.text` for email formatting

## Configuration Requirements
- Google Cloud Project with YouTube Data API enabled
- OAuth 2.0 credentials file (`client_secret.json`)
- Gmail app password for SMTP authentication
- Environment variables for sensitive configuration data