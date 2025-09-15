# Time-Based Prayer State Test Cases

This document outlines comprehensive test cases for determining prayer states based on various times throughout the day.

## Overview

The time-based prayer state tests verify that the application correctly determines prayer states (`future`, `pending`, `missed`, `completed`, `qada`) based on the current time relative to prayer time windows.

## Prayer Time Windows

Based on Islamic methodology, each prayer ends when the next prayer begins:

- **Fajr**: 05:21 - 12:15 (ends at Dhuhr)
- **Dhuhr**: 12:15 - 15:45 (ends at Asr)  
- **Asr**: 15:45 - 18:30 (ends at Maghrib)
- **Maghrib**: 18:30 - 19:45 (ends at Isha)
- **Isha**: 19:45 - 05:21 (ends at next day's Fajr)

## Test Scenarios

### 1. Fajr Prayer State Transitions

**Test Times:**
- 04:00 - Before Fajr time → `future` state
- 05:21 - At Fajr time → `pending` state  
- 06:30 - During Fajr window → `pending` state
- 10:00 - After Fajr window → `missed` state

**Expected Behaviors:**
- Before 05:21: Cannot complete, cannot mark as qada
- 05:21-12:15: Can complete, cannot mark as qada
- After 12:15: Cannot complete, can mark as qada

### 2. Dhuhr Prayer State Transitions

**Test Times:**
- 11:00 - Before Dhuhr time → `future` state
- 12:15 - At Dhuhr time → `pending` state
- 14:00 - During Dhuhr window → `pending` state  
- 15:45 - At Asr time (Dhuhr window ends) → `missed` state

**Expected Behaviors:**
- Before 12:15: Cannot complete, cannot mark as qada
- 12:15-15:45: Can complete, cannot mark as qada
- After 15:45: Cannot complete, can mark as qada

### 3. Asr Prayer State Transitions

**Test Times:**
- 14:00 - Before Asr time → `future` state
- 15:45 - At Asr time → `pending` state
- 17:00 - During Asr window → `pending` state
- 18:30 - At Maghrib time (Asr window ends) → `missed` state

**Expected Behaviors:**
- Before 15:45: Cannot complete, cannot mark as qada
- 15:45-18:30: Can complete, cannot mark as qada
- After 18:30: Cannot complete, can mark as qada

### 4. Maghrib Prayer State Transitions

**Test Times:**
- 17:00 - Before Maghrib time → `future` state
- 18:30 - At Maghrib time → `pending` state
- 19:00 - During Maghrib window → `pending` state
- 19:45 - At Isha time (Maghrib window ends) → `missed` state

**Expected Behaviors:**
- Before 18:30: Cannot complete, cannot mark as qada
- 18:30-19:45: Can complete, cannot mark as qada
- After 19:45: Cannot complete, can mark as qada

### 5. Isha Prayer State Transitions

**Test Times:**
- 18:00 - Before Isha time → `future` state
- 19:45 - At Isha time → `pending` state
- 22:00 - During Isha window → `pending` state
- 23:30 - Late night → `pending` state
- 03:00 - Early morning → `pending` state
- 05:20 - Just before Fajr → `missed` state

**Expected Behaviors:**
- Before 19:45: Cannot complete, cannot mark as qada
- 19:45-05:21: Can complete, cannot mark as qada
- After 05:21: Cannot complete, can mark as qada

### 6. Prayer Completion State Transitions

**Completion Scenarios:**
- Complete Fajr during its window → `completed` state (terminal)
- Try to complete Dhuhr after its window → Error + remains `missed`
- Mark missed Dhuhr as qada → `qada` state (terminal)

**Validation Rules:**
- Cannot complete same prayer twice
- Cannot mark completed prayer as qada
- Cannot mark qada prayer as qada again

### 7. Timezone-Aware Prayer State Transitions

**Test Timezones:**
- Asia/Kolkata (UTC+5:30)
- America/New_York (UTC-5/-4 with DST)
- Europe/London (UTC+0/+1 with DST)
- Asia/Dubai (UTC+4)

**Expected Behaviors:**
- Prayer times displayed in user's timezone
- State transitions based on user's local time
- Proper handling of daylight savings time

### 8. Edge Cases for Prayer State Transitions

**Precise Timing Tests:**
- 12:15:00 - Exactly at prayer start → `pending` state
- 15:45:00 - Exactly at prayer end → `pending` state
- 15:45:01 - One second after prayer end → `missed` state
- 12:14:59 - One second before prayer start → `future` state

**Validation:**
- Boundary conditions handled correctly
- Second-level precision maintained
- State transitions occur at exact boundaries

### 9. Midnight Prayer State Transitions

**Late Night/Early Morning Tests:**
- 23:59 - Late night Isha → `pending` state
- 00:30 - Early morning Isha → `pending` state
- 02:00 - Very early morning Isha → `pending` state
- 05:20 - Just before Fajr → `missed` state

**Validation:**
- Isha window extends across midnight
- Proper handling of day boundaries
- State transitions at dawn

### 10. Daylight Savings Time Prayer State Transitions

**DST Scenarios:**
- During daylight savings time
- After daylight savings ends
- Timezone transitions

**Expected Behaviors:**
- Prayer times account for DST changes
- State transitions remain accurate
- No double-counting or missed prayers

## Test Implementation

### Feature File
- **Location**: `features/prayer_tracking/time_based_prayer_states.feature`
- **Tags**: `@time-based`, `@api`, `@smoke`, `@completion`, `@timezone`, `@edge-cases`, `@midnight`, `@daylight-savings`

### Step Definitions
- **Location**: `features/steps/time_based_prayer_steps.py`
- **Key Steps**:
  - `I am logged in as a user with timezone "{timezone}"`
  - `the current time is "{time}" in my timezone`
  - `I check the {prayer_name} prayer status`
  - `the {prayer_name} prayer should be in "{status}" state`
  - `I should be able to complete the {prayer_name} prayer`
  - `I should not be able to complete the {prayer_name} prayer`
  - `I should be able to mark {prayer_name} as qada`
  - `I should not be able to mark {prayer_name} as qada`

## Running the Tests

```bash
# Run all time-based tests
python3 -m behave features/prayer_tracking/time_based_prayer_states.feature

# Run specific test scenarios
python3 -m behave features/prayer_tracking/time_based_prayer_states.feature --tags=@smoke
python3 -m behave features/prayer_tracking/time_based_prayer_states.feature --tags=@edge-cases
python3 -m behave features/prayer_tracking/time_based_prayer_states.feature --tags=@timezone

# Dry run to verify step definitions
python3 -m behave features/prayer_tracking/time_based_prayer_states.feature --dry-run
```

## Key Test Validations

1. **State Accuracy**: Prayer states match expected values based on time
2. **Action Permissions**: Correct actions allowed/denied based on state
3. **Timezone Handling**: Proper timezone conversion and display
4. **Boundary Conditions**: Exact timing boundaries handled correctly
5. **State Transitions**: Smooth transitions between states
6. **Error Handling**: Appropriate errors for invalid actions
7. **Terminal States**: Completed and qada prayers cannot be modified
8. **Cross-Day Logic**: Isha prayer window extends across midnight

## Benefits

These comprehensive test cases ensure:
- **Reliability**: Prayer states are always accurate
- **User Experience**: Users can trust the prayer tracking system
- **Islamic Compliance**: Prayer times follow proper Islamic methodology
- **Global Support**: Works correctly across all timezones
- **Edge Case Coverage**: Handles unusual timing scenarios
- **Maintainability**: Clear test structure for future updates
