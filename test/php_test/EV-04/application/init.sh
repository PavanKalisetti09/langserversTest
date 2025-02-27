#!/bin/bash
set -e

echo "🚀 Starting WordPress..."
docker-entrypoint.sh apache2-foreground &

echo "📌 Waiting for MariaDB to be ready..."
until wp db check --allow-root --path=/var/www/html; do
    echo "⏳ MariaDB is not ready yet. Retrying in 3 seconds..."
    sleep 3
done

echo "✅ MariaDB is ready. Running WordPress setup."

# Check if WordPress is installed
if wp core is-installed --allow-root --path=/var/www/html; then
    echo "✅ WordPress is already installed."
else
    echo "🚀 Installing WordPress..."
    wp core install --allow-root \
        --url="http://localhost:8080" \
        --title="${WORDPRESS_SITE_TITLE}" \
        --admin_user="${WORDPRESS_ADMIN_USER}" \
        --admin_password="${WORDPRESS_ADMIN_PASSWORD}" \
        --admin_email="${WORDPRESS_ADMIN_EMAIL}" \
        --path=/var/www/html

    echo "📌 Installing LearnPress..."
    wp plugin install /tmp/learnpress.zip --activate --allow-root --path=/var/www/html

    echo "✅ WordPress setup completed!"
fi
# 📌 Inject CTF flag from docker-compose.yml
if [ -n "$CTF_FLAG" ]; then
    echo "🚀 Creating hidden CTF challenge post with flag..."
    wp post create --post_title="Very secret post" \
                   --post_content="Flag: ${CTF_FLAG}" \
                   --post_status="draft" \
                   --post_author=1 \
                   --allow-root --path=/var/www/html
    echo "✅ Hidden post created with flag!"
else
    echo "⚠️ CTF_FLAG environment variable not set. Skipping hidden post."
fi

echo "🚀 Setup done. Keeping WordPress running..."
wait -n
