# Sample Data CSV Files

This directory contains CSV files used by the seed script to populate the database with test data.

## File Structure

### Core Entity Files

- **`users.csv`** - User accounts (admins and regular users)
  - The script will auto-generate 18 fake regular users if not enough are specified
  - Leave child fields empty to auto-generate with Faker
  - Example: `username,email,password,role,email_verified,first_name,last_name,child_name,child_sex_assigned_at_birth,child_dob,avatar_url`

- **`groups.csv`** - Groups
  - Requires `created_by_username` to reference a user from users.csv
  - Example: `name,description,created_by_username`

- **`courses.csv`** - Courses
  - Example: `title,description`

- **`modules.csv`** - Modules
  - Supports optional `color` field (hex color code, e.g., `#3B82F6`)
  - Example: `title,description,color`

- **`posts.csv`** - Posts
  - Supports `type` field: `post`, `post_file`, or `quiz`
  - Supports optional `content` field for markdown content
  - Example: `name,description,content,type`

### Relationship Files

- **`course_modules.csv`** - Links modules to courses with ordering
  - Example: `course_title,module_title,ordering`

- **`course_groups.csv`** - Assigns courses to groups
  - Example: `course_title,group_name,ordering,date_assigned`

- **`user_groups.csv`** - Adds users to groups with roles
  - Example: `username,group_name,role`
  - Note: Regular users are auto-assigned to groups if not specified

- **`module_posts.csv`** - Links posts to modules with ordering
  - Example: `module_title,post_name,ordering`

## Usage

1. Edit the CSV files to customize your seed data
2. Comments in CSV files start with `#` in the first column
3. Empty fields will be auto-generated where possible (e.g., child DOB, avatars)
4. Run the seed script: `python -m scripts.seed_data` or `python backend/scripts/populate.py`

## Tips

- Use consistent names/titles across relationship files (they're matched by name)
- Leave optional fields empty to use defaults or auto-generation
- The script will skip existing entities (based on unique constraints)
- Fake users are automatically generated to reach 18 total regular users

