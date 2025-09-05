Ubuntu Image Fetcher 🌍📸
A Python-based image downloader that embodies the Ubuntu philosophy of community, sharing, and respect. This tool mindfully collects images from the web while implementing safety precautions and duplicate prevention.

Features ✨
🔗 Multiple URL Support: Download multiple images in one session

🛡️ Safety First: Comprehensive security checks and validations

🔍 Duplicate Prevention: MD5 hash-based duplicate detection

📁 Organized Storage: Automatically creates "Fetched_Images" directory

⚡ Streaming Downloads: Efficient handling of large files

📊 Progress Tracking: Real-time download status and summary

🎯 Smart Filenaming: Extracts or generates appropriate filenames

❤️ Respectful Practices: Rate limiting and proper User-Agent headers

Installation 🚀
Clone the repository:

bash
git clone https://github.com/yourusername/ubuntu-image-fetcher.git
cd ubuntu-image-fetcher
Install required dependencies:

bash
pip install requests
Usage 💻
Run the script:

bash
python ubuntu_image_fetcher.py
Follow the prompts to enter image URLs (one per line). Press Enter twice to start downloading.

Safety Features 🛡️
URL scheme validation (HTTP/HTTPS only)

Content-Type verification for images

File size limits with user confirmation

Filename sanitization to prevent path traversal

Streaming downloads with size limits

User confirmation for suspicious downloads

Example Output 📝
text
============================================================
Welcome to the Ubuntu Image Fetcher
A tool for mindfully collecting images from the web
============================================================

Enter image URLs (one per line). Press Enter twice to finish:
https://example.com/image1.jpg
https://example.com/image2.png

Starting download of 2 image(s)...

--- Downloading image 1/2 ---
🔗 Connecting to: example.com
✓ Successfully fetched: image1.jpg
✓ Image saved to Fetched_Images/image1.jpg
✓ File size: 245.8KB

---

--- Downloading image 2/2 ---
🔗 Connecting to: example.com
✓ Image already downloaded (duplicate detected)

---

============================================================
DOWNLOAD SUMMARY
============================================================
Total URLs processed: 2
Successfully downloaded: 1
Failed: 1

✓ Connection strengthened. Community enriched.
✓ Images are ready for sharing and appreciation.
