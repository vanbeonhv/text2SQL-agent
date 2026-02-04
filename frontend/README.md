# Text2SQL Agent Frontend

Modern React 18 chatbot interface with AI Modern theme (purple-cyan) for the Text2SQL Agent.

## Features

- ✨ **Modern UI**: AI Modern theme with purple-cyan color scheme
- 🌓 **Dark/Light Mode**: System preference detection with manual toggle
- 📱 **Fully Responsive**: Desktop, tablet, and mobile with overlay sidebars
- 🎨 **Syntax Highlighting**: Shiki-powered SQL syntax highlighting
- 📊 **Process Visualizer**: Real-time SSE streaming with stage timeline
- ⌨️ **Keyboard Shortcuts**: Navigate efficiently with keyboard
- ♿ **Accessible**: WCAG AA compliant with ARIA labels and keyboard navigation

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Query** - Server state management
- **Shiki** - Code syntax highlighting
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (recommended)

### Installation

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env

# Update .env with your backend URL
# VITE_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview
```

## Project Structure

```
src/
├── app/                    # App setup
│   └── providers.tsx      # React Query provider
├── components/
│   ├── chat/              # Chat message components
│   ├── layout/            # Layout components (Topbar, Sidebars)
│   ├── sql/               # SQL code block with Shiki
│   ├── ui/                # Reusable UI components
│   └── visualizer/        # Process visualization components
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities
├── services/              # API services
├── stores/                # Zustand stores
├── styles/                # Global styles
└── types/                 # TypeScript types
```

## Keyboard Shortcuts

- `Cmd/Ctrl + K` - New chat
- `Cmd/Ctrl + [` - Toggle left sidebar
- `Cmd/Ctrl + ]` - Toggle right sidebar
- `Escape` - Close overlays
- `Enter` - Send message
- `Shift + Enter` - New line in message

## Theme Configuration

The app uses a custom AI Modern theme with:

- **Primary**: Purple (#7C3AED)
- **Secondary**: Light Purple (#A78BFA)
- **Accent**: Cyan (#06B6D4)
- **Success**: Emerald (#10B981)
- **Warning**: Amber (#F59E0B)
- **Error**: Rose (#F43F5E)

Colors automatically adapt for light and dark modes.

## API Integration

The frontend expects the following backend endpoints:

- `POST /api/chat/stream` - SSE streaming chat endpoint
- `GET /api/conversations/{id}` - Get conversation by ID
- `GET /api/health` - Health check

Configure the backend URL in `.env`:

```env
VITE_API_URL=http://localhost:8000
```

## SSE Events

The frontend handles these SSE event types from the backend:

- `conversation_id` - Conversation UUID
- `stage` - Processing stage updates
- `intent` - Detected user intent
- `schema` - Database schema
- `similar_examples` - Few-shot examples
- `sql` - Generated SQL query
- `validation` - SQL validation results
- `result` - Query execution results
- `error` - Error messages
- `complete` - Completion status

## Accessibility

The application follows WCAG 2.1 AA guidelines:

- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Screen reader support
- Respects `prefers-reduced-motion`
- Color contrast ratios meet standards

## Performance

- Code splitting with React lazy loading
- Memoized components
- Virtual scrolling for long lists
- Debounced search inputs
- Optimized re-renders with Zustand

## License

MIT
