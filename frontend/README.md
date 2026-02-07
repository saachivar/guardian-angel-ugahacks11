# Guardian Angel - Fall Detection iOS App

A Flutter fall detection and emergency alert app for iOS devices.

## Features

- **PairingScreen**: Device connection interface with paired devices and connection status
- **FeedScreen**: Real-time fall alert feed with emergency contact management  
- **ProfileScreen**: User settings and emergency contact configuration
- **Bottom Navigation**: Three-tab interface with red Guardian Angel branding
- **Mock Data**: Simulated fall alerts, device connections, and emergency contacts for testing

## Technical Implementation

- Flutter app with Material Design and iOS-specific configurations
- StatefulWidget architecture with proper state management
- Custom red color scheme matching Guardian Angel branding
- iOS-ready build configuration
- Complete app contained in single `main.dart` file

## Development Environment

- **Flutter SDK**: 3.38.9 (Channel stable)
- **Xcode**: 26.2 (Build 17C52) 
- **iOS Simulator**: "Guardian Angel Test" (iPhone 15 simulator)
- **Repository**: saachivar/guardian-angel-ugahacks11
- **Branch**: tmp-working-version

## Getting Started

### Prerequisites
- Flutter SDK 3.38.9 or higher
- Xcode with iOS simulator
- iOS device or simulator for testing

### Setup
```bash
# Install dependencies
flutter pub get

# Run on iOS simulator
flutter run -d "Guardian Angel Test"

# Build for iOS
flutter build ios --simulator
```

### Development Commands
```bash
# Hot reload during development
r (while app is running)

# Hot restart
R (while app is running)

# Build for iOS simulator
flutter build ios --simulator

# Check available devices
flutter devices
```

### Project Structure
- `lib/main.dart` - Complete Guardian Angel app implementation (12,235 bytes)
- `ios/` - iOS-specific configuration
- `android/` - Android platform support
- `pubspec.yaml` - Flutter dependencies and project configuration

### Workspace Information
- **Location**: `/Users/anishakumar/empty`
- **Status**: ✅ Verified working iOS build environment
- **Build Performance**: ~30 second iOS builds
- **Features**: Hot reload enabled, Flutter DevTools available

## Architecture

The app uses a simple three-screen bottom navigation structure:
1. **Pairing Screen** - Device management and connection status
2. **Feed Screen** - Fall alert notifications and emergency contacts
3. **Profile Screen** - User settings and configuration

All screens use mock data for demonstration and testing purposes.
