# GET vs. POST: The Delivery Methods

When your website talks to your AI server, it uses "HTTP Methods". Think of these as different ways to send a message.

## 1. GET (The Postcard) ✉️
- **How it works**: Data is attached to the end of the URL. (e.g., `google.com/search?q=AI`)
- **Visual**: Like a postcard. Anyone handling the mail can see what's written on it.
- **Limit**: URLs can't be too long (usually ~2000 characters). 
- **Usage**: Good for simple searches or getting a page.

## 2. POST (The Letter in an Envelope) ✉️📂
- **How it works**: Data is hidden inside the "body" of the message.
- **Visual**: Like a letter inside a sealed envelope. It's more private and can hold a lot more.
- **Limit**: Virtually no limit! You can send an entire book this way.
- **Usage**: Perfect for our project because Resumes and Transcripts are **huge**!

---
### 💡 Why we use POST in your UI:
1. **Length**: A 5-page resume would break a GET request's URL limit.
2. **Security**: Even though this is a school project, using POST is the "Professional Way" to send user data.
