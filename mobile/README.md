# Mobile App - Three Moves Ahead

React Native mobile application for users to access their groups, courses, and track progress. Built with Expo, React Native Paper, and TypeScript.

## Features

- **Authentication**: Secure login with token-based authentication
- **Groups**: View groups you belong to
- **Courses**: Browse and access courses assigned to your groups
- **Modules & Posts**: Navigate through course modules and view content
- **Quizzes**: Take quizzes with multiple question types (multiple choice, checkbox, text, true/false)
- **Progress Tracking**: Track completion of posts and view overall progress
- **File Downloads**: Download and view file posts

## Tech Stack

- **Expo**: React Native framework
- **Expo Router**: File-based routing
- **React Native Paper**: Material Design 3 UI components
- **TypeScript**: Type safety
- **React Query**: Data fetching and caching
- **Axios**: HTTP client
- **Expo Secure Store**: Secure token storage

## Prerequisites

- Node.js 18.17.0 (see `.nvmrc`)
- npm or yarn
- Expo CLI (installed globally or via npx)
- iOS Simulator (for iOS development) or Android Emulator (for Android development)

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment variables**:
   Create a `.env` file in the `mobile/` directory:
   ```
   EXPO_PUBLIC_API_URL=http://localhost:8000
   ```
   Update the URL to match your backend API.

3. **Start the development server**:
   ```bash
   npm start
   ```

4. **Run on device/simulator**:
   - iOS: `npm run ios`
   - Android: `npm run android`
   - Web: `npm run web`

## Project Structure

```
mobile/
├── app/                    # Expo Router app directory
│   ├── (auth)/            # Authentication screens
│   ├── (tabs)/            # Tab navigation screens
│   ├── courses/            # Course detail screens
│   ├── modules/            # Module detail screens
│   ├── posts/              # Post viewing screens
│   ├── files/              # File viewing screens
│   └── quizzes/            # Quiz taking screens
├── components/             # Reusable components
├── contexts/               # React contexts (Auth)
├── services/               # API service layer
├── types/                  # TypeScript type definitions
├── theme.ts               # React Native Paper theme
└── README.md
```

## Development Workflow

1. **Start backend server**: Ensure the FastAPI backend is running
2. **Start Expo dev server**: `npm start`
3. **Open in simulator/emulator**: Press `i` for iOS or `a` for Android
4. **Make changes**: Files are hot-reloaded automatically

## Environment Variables

- `EXPO_PUBLIC_API_URL`: Backend API URL
  - **Android emulator**: Automatically uses `http://10.0.2.2:8000` (to access host machine's localhost)
  - **iOS simulator**: Uses `http://localhost:8000`
  - **Physical devices**: Set to your computer's IP address (e.g., `http://192.168.1.100:8000`)
  - **Web**: Uses `http://localhost:8000`

See `NETWORK_SETUP.md` for detailed network configuration guide.

## Building for Production

### iOS

1. **Configure app.json**: Update bundle identifier and other iOS-specific settings
2. **Build**:
   ```bash
   eas build --platform ios
   ```
   Or use Expo's build service.

### Android

1. **Configure app.json**: Update package name and other Android-specific settings
2. **Build**:
   ```bash
   eas build --platform android
   ```
   Or use Expo's build service.

## Design System

The app uses **React Native Paper** with a custom theme matching the web app's color scheme:

- **Primary Color**: `#009EB1` (Cyan-blue)
- **Secondary Color**: `#B44985` (Pink-magenta)
- **Error**: `#DC2626` (Red)
- **Success**: `#10B981` (Green)

Theme configuration is in `theme.ts`.

## API Integration

The app connects to the FastAPI backend using the following endpoints:

- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `GET /api/groups` - Get user's groups
- `GET /api/courses/{id}` - Get course details
- `GET /api/modules/{id}` - Get module details
- `GET /api/module-posts?module_id={id}` - Get posts in module
- `GET /api/posts/{id}` - Get post content
- `GET /api/quizzes/{id}` - Get quiz
- `POST /api/quiz-attempts` - Start quiz attempt
- `POST /api/quiz-attempts/{id}/submit` - Submit quiz
- `GET /api/user-progress` - Get user progress
- `POST /api/user-progress` - Create progress record

## Authentication

- Tokens are stored securely using `expo-secure-store`
- Automatic token injection in API requests
- Automatic logout on 401 responses
- Protected routes check authentication status

## User Role Restrictions

This mobile app is designed for users with the "user" role only. Admin users are blocked from accessing the app.

## Troubleshooting

### Metro bundler issues
```bash
npm start -- --reset-cache
```

### iOS build issues
- Ensure Xcode and iOS Simulator are installed
- Check that CocoaPods dependencies are installed (if using bare workflow)

### Android build issues
- Ensure Android Studio and Android SDK are installed
- Check that ANDROID_HOME is set correctly

## License

ISC

