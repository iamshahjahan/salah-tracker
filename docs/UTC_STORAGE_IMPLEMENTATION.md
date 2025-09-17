# UTC Storage Implementation

This document describes the comprehensive UTC storage implementation across all models in the Salah Tracker application.

## Overview

All datetime fields in the application are now stored in UTC format to ensure consistency, avoid timezone-related bugs, and provide a solid foundation for international users. The implementation includes:

- **UTC Storage**: All datetime fields are stored in UTC timezone
- **Timezone Conversion**: Utility methods for converting between UTC and local timezones
- **User-Specific Localization**: Automatic conversion to user's preferred timezone
- **Consistent API**: Standardized methods across all models

## Models Updated

### 1. User Model (`app/models/user.py`)
- `created_at`: Stored in UTC, can be localized to user's timezone
- `updated_at`: Stored in UTC, can be localized to user's timezone
- **New Methods**:
  - `localized_created_at()`: Returns created_at in user's timezone
  - `utc_created_at()`: Returns created_at in UTC
  - `localized_updated_at()`: Returns updated_at in user's timezone
  - `utc_updated_at()`: Returns updated_at in UTC

### 2. Prayer Model (`app/models/prayer.py`)
- `created_at`: Stored in UTC
- **New Methods**:
  - `localized_prayer_datetime()`: Returns prayer time in user's timezone
  - `utc_prayer_datetime()`: Returns prayer time in UTC
  - `localized_created_at()`: Returns created_at in user's timezone
  - `utc_created_at()`: Returns created_at in UTC

### 3. PrayerCompletion Model (`app/models/prayer.py`)
- `marked_at`: Stored in UTC
- **New Methods**:
  - `localized_marked_at()`: Returns marked_at in prayer's timezone
  - `utc_marked_at()`: Returns marked_at in UTC

### 4. FamilyMember Model (`app/models/family.py`)
- `created_at`: Stored in UTC
- `updated_at`: Stored in UTC
- **New Methods**:
  - `localized_created_at()`: Returns created_at in user's timezone
  - `utc_created_at()`: Returns created_at in UTC
  - `localized_updated_at()`: Returns updated_at in user's timezone
  - `utc_updated_at()`: Returns updated_at in UTC

### 5. FamilyGroup Model (`app/models/family_group.py`)
- `created_at`: Stored in UTC
- `updated_at`: Stored in UTC
- **New Methods**:
  - `localized_created_at()`: Returns created_at in admin user's timezone
  - `utc_created_at()`: Returns created_at in UTC
  - `localized_updated_at()`: Returns updated_at in admin user's timezone
  - `utc_updated_at()`: Returns updated_at in UTC

### 6. FamilyGroupMember Model (`app/models/family_group.py`)
- `joined_at`: Stored in UTC
- **New Methods**:
  - `localized_joined_at()`: Returns joined_at in user's timezone
  - `utc_joined_at()`: Returns joined_at in UTC

### 7. PrayerNotification Model (`app/models/prayer_notification.py`)
- `sent_at`: Stored in UTC
- `created_at`: Stored in UTC
- **New Methods**:
  - `localized_sent_at()`: Returns sent_at in user's timezone
  - `utc_sent_at()`: Returns sent_at in UTC
  - `localized_created_at()`: Returns created_at in user's timezone
  - `utc_created_at()`: Returns created_at in UTC

### 8. EmailVerification Model (`app/models/email_verification.py`)
- `expires_at`: Stored in UTC
- `created_at`: Stored in UTC
- **New Methods**:
  - `localized_expires_at()`: Returns expires_at in user's timezone
  - `utc_expires_at()`: Returns expires_at in UTC
  - `localized_created_at()`: Returns created_at in user's timezone
  - `utc_created_at()`: Returns created_at in UTC

### 9. Inspirational Content Models (`app/models/inspirational_content.py`)
- `QuranicVerse.created_at`: Stored in UTC
- `Hadith.created_at`: Stored in UTC
- **New Methods**:
  - `utc_created_at()`: Returns created_at in UTC (for both models)

## Timezone Utilities (`app/utils/timezone_utils.py`)

A comprehensive utility module provides consistent timezone handling:

### Core Functions
- `get_utc_now()`: Get current datetime in UTC
- `to_utc(dt, source_timezone)`: Convert datetime to UTC
- `to_local(dt, target_timezone)`: Convert UTC datetime to local timezone
- `format_datetime_utc(dt)`: Format datetime as ISO string in UTC
- `format_datetime_local(dt, timezone)`: Format datetime as ISO string in local timezone
- `parse_utc_datetime(dt_string)`: Parse datetime string and return as UTC
- `get_timezone_offset(timezone)`: Get current UTC offset for timezone
- `is_dst_active(timezone)`: Check if DST is active in timezone
- `validate_timezone(timezone)`: Validate timezone string

### TimezoneMixin Class
A mixin class that provides timezone utility methods to models:
- `get_user_timezone()`: Get user's timezone
- `to_utc_datetime(dt)`: Convert datetime to UTC
- `to_local_datetime(dt)`: Convert UTC datetime to local timezone
- `format_utc_datetime(dt)`: Format datetime as UTC ISO string
- `format_local_datetime(dt)`: Format datetime as local ISO string

## API Response Format

All `to_dict()` methods now include both local and UTC datetime formats:

```json
{
  "id": 1,
  "created_at": "2025-09-17T20:30:00+05:30",
  "created_at_utc": "2025-09-17T15:00:00+00:00",
  "updated_at": "2025-09-17T20:35:00+05:30",
  "updated_at_utc": "2025-09-17T15:05:00+00:00"
}
```

## Migration Script

A migration script (`scripts/migrate_to_utc.py`) is provided to convert existing data:

```bash
python3 scripts/migrate_to_utc.py
```

This script:
- Converts all naive datetime fields to UTC
- Preserves existing data integrity
- Updates all models systematically
- Provides detailed progress reporting

## Benefits

### 1. **Consistency**
- All datetime fields use the same storage format
- No timezone confusion in the database
- Predictable behavior across different environments

### 2. **International Support**
- Users in different timezones see times in their local timezone
- Prayer times are calculated correctly regardless of user location
- DST transitions are handled automatically

### 3. **Data Integrity**
- No data loss during timezone conversions
- Consistent sorting and filtering by datetime
- Reliable datetime comparisons

### 4. **Developer Experience**
- Clear separation between storage (UTC) and display (local)
- Utility functions for common timezone operations
- Consistent API across all models

## Usage Examples

### Creating Records with UTC Storage
```python
from app.utils.timezone_utils import get_utc_now

# Create a new prayer completion
completion = PrayerCompletion(
    user_id=1,
    prayer_id=1,
    marked_at=get_utc_now(),  # Automatically stored in UTC
    status=PrayerCompletionStatus.JAMAAT
)
```

### Converting to User's Timezone
```python
# Get prayer completion in user's timezone
completion = PrayerCompletion.query.get(1)
local_time = completion.localized_marked_at()
utc_time = completion.utc_marked_at()

print(f"Local time: {local_time}")
print(f"UTC time: {utc_time}")
```

### Using Timezone Utilities
```python
from app.utils.timezone_utils import to_utc, to_local, get_utc_now

# Convert user input to UTC for storage
user_input = "2025-09-17 20:30:00"
user_timezone = "Asia/Kolkata"
utc_time = to_utc(datetime.fromisoformat(user_input), user_timezone)

# Convert UTC to user's timezone for display
display_time = to_local(utc_time, user_timezone)
```

## Best Practices

### 1. **Always Store in UTC**
```python
# ✅ Good
created_at = get_utc_now()

# ❌ Bad
created_at = datetime.now()  # Naive datetime
```

### 2. **Convert for Display**
```python
# ✅ Good
def get_user_prayers(user_id):
    prayers = Prayer.query.filter_by(user_id=user_id).all()
    return [prayer.to_dict() for prayer in prayers]  # Includes both local and UTC

# ❌ Bad
def get_user_prayers(user_id):
    prayers = Prayer.query.filter_by(user_id=user_id).all()
    return [{'time': prayer.prayer_time} for prayer in prayers]  # No timezone info
```

### 3. **Use Utility Functions**
```python
# ✅ Good
from app.utils.timezone_utils import get_utc_now, to_local

# ❌ Bad
from datetime import datetime
datetime.now()  # Inconsistent timezone handling
```

## Testing

The implementation includes comprehensive testing to ensure:
- UTC storage works correctly
- Timezone conversions are accurate
- DST transitions are handled properly
- API responses include both local and UTC times

## Future Enhancements

1. **Caching**: Cache timezone conversions for better performance
2. **Bulk Operations**: Optimize timezone conversions for bulk data operations
3. **Timezone Detection**: Automatically detect user timezone from browser/IP
4. **Prayer Time Integration**: Enhanced prayer time calculations with timezone awareness

## Conclusion

The UTC storage implementation provides a robust foundation for handling datetime data across different timezones. It ensures data consistency, improves user experience, and simplifies development by providing clear patterns for timezone handling throughout the application.
