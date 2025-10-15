#!/bin/bash

# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-venv nginx python3-dev

# Clone repository
git clone https://github.com/10Soumyajit/visual-matcher.git
cd visual-matcher

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup systemd service
sudo cp visual-matcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable visual-matcher
sudo systemctl start visual-matcher

# Configure Nginx
sudo bash -c 'cat > /etc/nginx/sites-available/visual-matcher <<EOF
server {
    listen 80;
    server_name YOUR_SERVER_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF'

# Enable the Nginx site
sudo ln -s /etc/nginx/sites-available/visual-matcher /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx