import requests
import os
import hashlib
import mimetypes
from urllib.parse import urlparse
from pathlib import Path
import time

class UbuntuImageFetcher:
    def __init__(self):
        self.downloaded_hashes = set()
        self.fetched_dir = "Fetched_Images"
        
    def create_directory(self):
        """Create the directory for storing images"""
        os.makedirs(self.fetched_dir, exist_ok=True)
        print(f"✓ Directory '{self.fetched_dir}' is ready")
    
    def validate_url(self, url):
        """Basic URL validation"""
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid URL format")
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Only HTTP/HTTPS URLs are supported")
        return True
    
    def get_filename_from_url(self, url, content_type=None):
        """Extract or generate appropriate filename"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        if not filename or '.' not in filename:
            # Generate filename based on content type or default
            extension = self.get_extension_from_content_type(content_type)
            timestamp = int(time.time())
            filename = f"ubuntu_image_{timestamp}{extension}"
        
        # Sanitize filename to prevent path traversal
        filename = self.sanitize_filename(filename)
        
        return filename
    
    def get_extension_from_content_type(self, content_type):
        """Get file extension from content type"""
        if content_type:
            extension = mimetypes.guess_extension(content_type.split(';')[0])
            if extension:
                return extension
        
        # Default extension if content type is unknown
        return ".jpg"
    
    def sanitize_filename(self, filename):
        """Sanitize filename to prevent path traversal and special characters"""
        # Remove directory traversal attempts
        filename = os.path.basename(filename)
        # Replace potentially problematic characters
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        return filename or "downloaded_image.jpg"
    
    def calculate_file_hash(self, content):
        """Calculate MD5 hash of file content for duplicate detection"""
        return hashlib.md5(content).hexdigest()
    
    def is_duplicate(self, content_hash):
        """Check if file has already been downloaded"""
        return content_hash in self.downloaded_hashes
    
    def load_existing_hashes(self):
        """Load hashes of already downloaded files"""
        try:
            for file in Path(self.fetched_dir).glob('*'):
                if file.is_file():
                    with open(file, 'rb') as f:
                        content = f.read()
                        self.downloaded_hashes.add(self.calculate_file_hash(content))
        except Exception:
            # If we can't load existing hashes, continue without duplicate checking
            pass
    
    def check_http_headers(self, response):
        """Check important HTTP headers before downloading"""
        headers_to_check = {
            'Content-Type': response.headers.get('Content-Type', ''),
            'Content-Length': response.headers.get('Content-Length', '0'),
            'X-Content-Type-Options': response.headers.get('X-Content-Type-Options', ''),
        }
        
        # Check if content type is an image
        content_type = headers_to_check['Content-Type'].lower()
        if not content_type.startswith('image/'):
            print(f"⚠ Warning: Content-Type is '{content_type}', expected an image")
            # Ask for confirmation to continue
            if not self.confirm_download("This doesn't appear to be an image. Continue?"):
                raise ValueError("Download cancelled by user")
        
        # Check content length (prevent huge downloads)
        try:
            content_length = int(headers_to_check['Content-Length'])
            if content_length > 50 * 1024 * 1024:  # 50MB limit
                if not self.confirm_download(f"File is large ({content_length/1024/1024:.1f}MB). Continue?"):
                    raise ValueError("Download cancelled due to large file size")
        except ValueError:
            pass
        
        return headers_to_check
    
    def confirm_download(self, message):
        """Ask user for confirmation"""
        response = input(f"{message} (y/N): ").lower().strip()
        return response in ['y', 'yes']
    
    def download_image(self, url):
        """Download a single image with safety checks"""
        try:
            # Validate URL
            self.validate_url(url)
            
            # Make request with safe headers and timeout
            headers = {
                'User-Agent': 'UbuntuImageFetcher/1.0 (Community Image Collector)'
            }
            
            print(f"🔗 Connecting to: {urlparse(url).netloc}")
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check HTTP headers for safety
            http_info = self.check_http_headers(response)
            
            # Read content in chunks for large files
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                # Safety check: don't download more than 100MB
                if len(content) > 100 * 1024 * 1024:
                    raise ValueError("File too large (over 100MB)")
            
            # Check for duplicates
            content_hash = self.calculate_file_hash(content)
            if self.is_duplicate(content_hash):
                print("✓ Image already downloaded (duplicate detected)")
                return None
            
            # Get appropriate filename
            filename = self.get_filename_from_url(url, http_info['Content-Type'])
            filepath = os.path.join(self.fetched_dir, filename)
            
            # Ensure unique filename
            counter = 1
            base_name, extension = os.path.splitext(filename)
            while os.path.exists(filepath):
                filename = f"{base_name}_{counter}{extension}"
                filepath = os.path.join(self.fetched_dir, filename)
                counter += 1
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(content)
            
            # Add to downloaded hashes
            self.downloaded_hashes.add(content_hash)
            
            print(f"✓ Successfully fetched: {filename}")
            print(f"✓ Image saved to {filepath}")
            
            file_size = len(content)
            print(f"✓ File size: {file_size/1024:.1f}KB")
            
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
        except ValueError as e:
            print(f"✗ Validation error: {e}")
        except Exception as e:
            print(f"✗ An unexpected error occurred: {e}")
        
        return None
    
    def download_multiple_images(self, urls):
        """Download multiple images from a list of URLs"""
        successful_downloads = 0
        
        for i, url in enumerate(urls, 1):
            url = url.strip()
            if not url:
                continue
                
            print(f"\n--- Downloading image {i}/{len(urls)} ---")
            result = self.download_image(url)
            if result:
                successful_downloads += 1
            print("-" * 40)
            time.sleep(1)  # Be respectful to servers
        
        return successful_downloads
    
    def get_urls_from_user(self):
        """Get URLs from user input"""
        print("\nEnter image URLs (one per line). Press Enter twice to finish:")
        urls = []
        
        while True:
            try:
                line = input().strip()
                if not line:
                    if urls:  # Empty line after URLs means finish
                        break
                    continue
                urls.append(line)
            except EOFError:
                break
        
        return urls

def main():
    print("=" * 60)
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web")
    print("=" * 60)
    
    fetcher = UbuntuImageFetcher()
    
    try:
        # Create directory and load existing hashes
        fetcher.create_directory()
        fetcher.load_existing_hashes()
        
        # Get URLs from user
        urls = fetcher.get_urls_from_user()
        
        if not urls:
            print("No URLs provided. Exiting.")
            return
        
        print(f"\nStarting download of {len(urls)} image(s)...")
        
        # Download images
        successful = fetcher.download_multiple_images(urls)
        
        # Summary
        print("\n" + "=" * 60)
        print("DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"Total URLs processed: {len(urls)}")
        print(f"Successfully downloaded: {successful}")
        print(f"Failed: {len(urls) - successful}")
        
        if successful > 0:
            print("\n✓ Connection strengthened. Community enriched.")
            print("✓ Images are ready for sharing and appreciation.")
        else:
            print("\n⚠ No images were downloaded. Please check the URLs.")
            
    except KeyboardInterrupt:
        print("\n\n⏹ Download process interrupted by user.")
    except Exception as e:
        print(f"\n✗ A critical error occurred: {e}")

if __name__ == "__main__":
    main()