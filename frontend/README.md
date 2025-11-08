# Ripple Frontend

A mobile-first React application for the Ripple fundraising platform, featuring authentication, giver profile management, and comprehensive testing.

## Features

- **Authentication**: User registration and login with JWT tokens
- **Giver Profile Management**: View and update personal information and address details
- **Donation History**: View past donations and total contribution
- **Mobile-First Design**: Responsive design optimised for mobile devices
- **Comprehensive Testing**: Full test coverage with Vitest and React Testing Library

## Colour Palette

- Primary Green: `#89B87A`
- Secondary Teal: `#6ABEA9`
- Accent Burgundy: `#933950`
- Dark Charcoal: `#2C2F23`

## Technology Stack

- **React 18**: UI library
- **Vite**: Build tool and development server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API requests
- **Vitest**: Unit testing framework
- **React Testing Library**: Component testing utilities

## Prerequisites

- Node.js (v18 or higher recommended)
- npm or yarn
- Backend API running on http://localhost:8000

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your backend API URL if different from default:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## Testing

Run all tests:
```bash
npm test
```

Run tests in watch mode:
```bash
npm test -- --watch
```

Run tests with UI:
```bash
npm run test:ui
```

Generate coverage report:
```bash
npm run test:coverage
```

## Building for Production

Build the application:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Project Structure

```
qfrontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable React components
│   │   └── Header.jsx    # Navigation header
│   ├── contexts/         # React contexts
│   │   └── AuthContext.jsx   # Authentication context
│   ├── pages/           # Page components
│   │   ├── Login.jsx       # Login page
│   │   ├── Register.jsx    # Registration page
│   │   ├── Profile.jsx     # User profile page
│   │   └── Dashboard.jsx   # Dashboard page
│   ├── services/        # API services
│   │   └── api.js          # API client and endpoints
│   ├── test/           # Test utilities
│   │   ├── setup.js        # Test setup and configuration
│   │   └── testUtils.js    # Test helpers and mocks
│   ├── App.jsx         # Main app component with routing
│   ├── main.jsx       # Application entry point
│   └── index.css     # Global styles
├── index.html        # HTML entry point
├── vite.config.js   # Vite configuration
└── package.json    # Project dependencies and scripts
```

## Key Components

### Authentication Flow

1. User registers or logs in via `/register` or `/login`
2. On successful authentication, JWT token is stored in localStorage
3. Token is automatically included in all API requests via axios interceptors
4. Protected routes redirect to login if user is not authenticated

### API Integration

The application communicates with the backend API through the `api.js` service layer:

- **Authentication**: Register, login, get current user
- **Giver Profiles**: Get and update profile, view donation history
- **Campaigns**: Create, read, update, delete campaigns (ready for implementation)
- **Donations**: Create and manage donations (ready for implementation)

### Mobile-First Design

All components are built with a mobile-first approach:
- Touch-friendly targets (minimum 44px height)
- Responsive layouts with CSS Grid and Flexbox
- Optimised form inputs for mobile devices
- Progressive enhancement for larger screens

## Testing Strategy

The application includes comprehensive tests for:

- **Component Testing**: Login, Register, Profile pages
- **Context Testing**: AuthContext authentication logic
- **Integration Testing**: Form submissions, API interactions
- **Validation Testing**: Form validation logic

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

## API Endpoints Used

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Giver Profiles
- `GET /givers/me` - Get current user's giver profile
- `PUT /givers/me` - Update current user's giver profile
- `GET /givers/me/donations` - Get current user's donation history

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile Safari (iOS 12+)
- Chrome Mobile (Android 8+)

## Future Development

The frontend is ready for the following features to be implemented:

- Campaign browsing and search
- Campaign creation and management
- Donation processing with Stripe integration
- Real-time updates for campaign progress
- Email notifications
- Social sharing functionality

## Contributing

When contributing to this project:

1. Write tests for new features
2. Maintain mobile-first design principles
3. Follow the established code style
4. Update documentation as needed
5. Use conventional commit messages

## Licence

This project is part of the Ripple fundraising platform.

---

Built with ❤️ by David "Bing" Crosby
