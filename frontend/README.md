# Face Login System - Frontend

This is the React-based frontend for the Face Login System, providing a user-friendly interface for face registration and authentication.

## Features

- **Dashboard**: Overview of system statistics and recent activity
- **User Management**: Create, update, and delete users
- **Face Registration**: Register face images for users using webcam
- **Face Authentication**: Authenticate users using facial recognition
- **History**: View authentication logs and export data

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running on http://localhost:5001

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

1. Make sure the backend Flask API is running on port 5001

2. Start the React development server:
```bash
npm start
```

3. Open your browser and navigate to http://localhost:3000

## Build for Production

To create a production build:
```bash
npm run build
```

The build files will be in the `build` directory.

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Layout.js         # Main layout with navigation
│   │   └── WebcamCapture.js  # Webcam component for face capture
│   ├── pages/
│   │   ├── Dashboard.js      # Dashboard page
│   │   ├── Users.js          # User management page
│   │   ├── Register.js       # Face registration page
│   │   ├── Authenticate.js   # Face authentication page
│   │   └── History.js        # Authentication history page
│   ├── services/
│   │   └── api.js           # API service for backend communication
│   ├── App.js               # Main app component with routing
│   ├── index.js             # Entry point
│   └── index.css            # Global styles with Tailwind CSS
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## Technologies Used

- **React 18**: UI framework
- **React Router v6**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Webcam**: Webcam integration

## API Integration

The frontend communicates with the backend API through the proxy configuration in `package.json`. All API calls are made to `/api/*` endpoints which are proxied to `http://localhost:5001`.

## Environment Variables

Create a `.env` file in the frontend directory if you need to customize settings:

```env
REACT_APP_API_URL=http://localhost:5001
```

## Browser Support

- Chrome (recommended for best webcam support)
- Firefox
- Safari
- Edge

## Troubleshooting

1. **Webcam not working**: Make sure you've granted camera permissions to the browser
2. **API connection errors**: Verify the backend is running on port 5001
3. **Build errors**: Clear node_modules and reinstall dependencies

## License

This project is part of the Face Login System.