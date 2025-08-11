# Formatic Frontend

Vue.js frontend for the Formatic dynamic form builder with FormKit and Tailwind CSS.

## Features

- **Dynamic Form Rendering**: Load and render forms from Django REST API
- **FormKit Integration**: Beautiful form components with validation
- **Tailwind CSS**: Modern, responsive UI design
- **Multi-page Forms**: Support for conditional logic and multi-step forms
- **Real-time Validation**: Client-side validation with server sync
- **Responsive Design**: Works on desktop and mobile devices

## Development

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Django backend running on `localhost:8000`

### Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open http://localhost:3000

### Build for Production

```bash
npm run build
```

Built files will be placed in `../static/frontend/` for Django integration.

## Project Structure

```
src/
├── components/          # Vue components
│   ├── DynamicForm.vue  # Main form renderer
│   └── FormList.vue     # Form listing component
├── views/               # Page components
│   ├── Home.vue         # Forms list page
│   └── FormView.vue     # Individual form page
├── services/            # API integration
│   └── api.js          # Django REST API client
├── plugins/            # Vue plugins
│   └── formkit.js      # FormKit configuration
├── router/             # Vue Router
└── style.css          # Tailwind CSS
```

## FormKit Integration

The frontend uses FormKit with custom Tailwind CSS styling for:

- Dynamic form field rendering
- Client-side validation
- Form submission handling
- Multi-step form navigation

## Django API Integration

The frontend communicates with Django via REST API:

- `GET /api/forms/` - List available forms
- `GET /api/forms/{slug}/` - Get form structure  
- `POST /api/submissions/` - Create form submission
- `PATCH /api/submissions/{id}/` - Update submission

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
VITE_API_URL=http://localhost:8000/api
```