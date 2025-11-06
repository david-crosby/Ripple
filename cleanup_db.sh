#!/bin/zsh

# Database cleanup script
# Removes test users and associated data from the database

set -e

echo "🧹 Ripple Database Cleanup"
echo "=========================="
echo ""

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if MySQL container is running
if ! docker ps | grep fundraiser_db >/dev/null 2>&1; then
    echo "❌ MySQL container (fundraiser_db) is not running."
    echo "   Run: docker-compose up -d"
    exit 1
fi

echo "⚠️  This will delete all test users (username starting with 'testuser_') and their:"
echo "   - Giver profiles"
echo "   - Campaigns"
echo "   - Donations"
echo ""
read -q "REPLY?Are you sure you want to continue? (y/n) "
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

echo ""
echo "🗑️  Deleting test data..."

# SQL commands to clean up test data
docker exec -i fundraiser_db mysql -u fundraiser_user -pfundraiser_pass fundraiser_dev << 'EOF'
-- Get count before deletion
SELECT COUNT(*) as test_user_count FROM users WHERE username LIKE 'testuser_%';

-- Delete in correct order (respecting foreign keys)
DELETE FROM donations WHERE giver_id IN (
    SELECT id FROM giver_profiles WHERE user_id IN (
        SELECT id FROM users WHERE username LIKE 'testuser_%'
    )
);

DELETE FROM campaigns WHERE creator_id IN (
    SELECT id FROM users WHERE username LIKE 'testuser_%'
);

DELETE FROM giver_profiles WHERE user_id IN (
    SELECT id FROM users WHERE username LIKE 'testuser_%'
);

DELETE FROM users WHERE username LIKE 'testuser_%';

-- Show remaining users
SELECT COUNT(*) as remaining_users FROM users;
EOF

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 To verify, you can check the database:"
echo "   docker exec -it fundraiser_db mysql -u fundraiser_user -pfundraiser_pass fundraiser_dev"
echo "   Then run: SELECT username FROM users;"