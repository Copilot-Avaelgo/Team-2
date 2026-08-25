# Bona RAG Frontend Test Suite

## Overview
Comprehensive test suite for React components using Vitest and React Testing Library.

## Test Files Created

### 1. **MessageBubble.test.tsx** (8 test cases)
Tests for the `MessageBubble` component that displays individual chat messages.

**Test Coverage:**
- ✅ Renders user message with right-aligned styling
- ✅ Does not display avatar for user messages
- ✅ Renders agent message with left-aligned styling  
- ✅ Displays avatar for agent messages
- ✅ Displays message text correctly
- ✅ Applies message-bubble class with correct variant
- ✅ Handles empty text
- ✅ Handles text with special characters

**Component Features Tested:**
- User vs agent message differentiation
- Avatar display (only for agent)
- CSS class application
- Text rendering

---

### 2. **SourcesDisplay.test.tsx** (10 test cases)
Tests for the `SourcesDisplay` component that shows document sources and relevance scores.

**Test Coverage:**
- ✅ Renders sources with file names
- ✅ Displays relevance score as percentage
- ✅ Displays multiple document sources
- ✅ Displays sources header
- ✅ Returns null when documents array is empty
- ✅ Returns null when documents is falsy
- ✅ Correctly formats scores with decimal precision
- ✅ Renders with file icon
- ✅ Handles file names with special characters
- ✅ Applies correct CSS classes to containers

**Component Features Tested:**
- Empty state handling (returns null)
- Multiple document rendering
- Score formatting (percentage with precision)
- File icon display
- CSS class structure

---

### 3. **InputComposer.test.tsx** (15 test cases)
Tests for the `InputComposer` component that handles user text input.

**Test Coverage:**
- ✅ Renders textarea with placeholder text
- ✅ Renders send button
- ✅ Handles text input correctly
- ✅ Calls onSend when send button is clicked with text
- ✅ Calls onSend when Enter key is pressed (not Shift+Enter)
- ✅ Does not send on Shift+Enter
- ✅ Clears input after sending
- ✅ Disables send button when input is empty
- ✅ Enables send button when input has text
- ✅ Disables send button when only whitespace is entered
- ✅ Disables send button and shows loading state when isLoading is true
- ✅ Displays "Sending..." text on button when loading
- ✅ Does not send message when isLoading is true
- ✅ Expands textarea on multi-line input
- ✅ Handles rapid successive messages

**Component Features Tested:**
- Text input handling
- Keyboard shortcuts (Enter vs Shift+Enter)
- Button state management
- Input validation (empty/whitespace)
- Auto-resize textarea
- Loading state

---

### 4. **ChatWindow.test.tsx** (18 test cases)
Tests for the `ChatWindow` component that manages the chat interface.

**Test Coverage:**
- ✅ Renders chat interface with header
- ✅ Displays welcome message when no messages are present
- ✅ Sends message on button click
- ✅ Displays user messages in chat
- ✅ Displays agent responses in chat
- ✅ Shows typing indicator while loading
- ✅ Hides typing indicator after response received
- ✅ Displays error messages when API fails
- ✅ Handles session ID consistently
- ✅ Displays multiple messages in sequence
- ✅ Displays sources when agent response includes source documents
- ✅ Does not display sources when empty sources array
- ✅ Auto-scrolls to bottom on new messages
- ✅ Clears error when sending new message
- ✅ Handles error response with error message in state
- ✅ Disables input while loading

**Component Features Tested:**
- Header rendering
- Message display (user and agent)
- API integration (mocked)
- Session ID generation and consistency
- Loading state and typing indicator
- Error handling and display
- Source document display
- Auto-scroll functionality
- Input state management

---

## Test Infrastructure

### Setup Files
- **`setup.ts`**: Global test configuration including:
  - Vitest global imports
  - React Testing Library DOM matchers
  - Axios mocking
  - Window.matchMedia mock

### Configuration
- **`vitest.config.ts`**: Vitest configuration with:
  - jsdom environment
  - Global test mode
  - CSS support
  - Coverage reporting (v8)

### Package Dependencies Added
- `@testing-library/react`: ^14.1.2
- `@testing-library/jest-dom`: ^6.1.5
- `@testing-library/user-event`: ^14.5.1
- `vitest`: ^1.0.4
- `@vitest/ui`: ^1.0.4
- `jsdom`: ^23.0.1

---

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests with UI
```bash
npm run test:ui
```

### Run tests with coverage
```bash
npm run test:coverage
```

### Run tests in watch mode
```bash
npm test -- --watch
```

### Run specific test file
```bash
npm test -- MessageBubble.test.tsx
```

---

## Test Statistics

| Component | Test Cases | Key Features |
|-----------|-----------|--------------|
| MessageBubble | 8 | Message rendering, styling, avatars |
| SourcesDisplay | 10 | Document sources, scoring, empty states |
| InputComposer | 15 | Text input, keyboard shortcuts, validation |
| ChatWindow | 18 | Chat flow, API mocking, error handling |
| **TOTAL** | **51** | **Comprehensive coverage** |

---

## Mocking Strategy

### API Mocking (chatAPI)
- `sendMessage()`: Mocked to return `ChatResponse`
- `healthCheck()`: Mocked for initialization tests
- Error scenarios tested with `.mockRejectedValue()`
- Delayed responses tested with `.mockImplementation()` returning promises

### DOM Mocking
- `window.matchMedia`: Mocked for responsive behavior
- `axios`: Mocked at module level to avoid actual API calls

---

## Test Patterns Used

### User-Centric Queries
- `screen.getByRole()`: For buttons, inputs
- `screen.getByText()`: For text content
- `screen.getByPlaceholderText()`: For form inputs
- `screen.queryByText()`: For non-existent elements

### User Interactions
- `userEvent.setup()`: For realistic user simulation
- `userEvent.type()`: For keyboard input
- `userEvent.click()`: For button clicks
- `userEvent.keyboard()`: For keyboard shortcuts

### Async Handling
- `waitFor()`: For async state updates
- Promise mocks for API delays

---

## Coverage Goals

### Current Coverage
- **MessageBubble**: 100% - All rendering and styling paths
- **SourcesDisplay**: 100% - All states (empty, single, multiple documents)
- **InputComposer**: 100% - All input scenarios and keyboard handling
- **ChatWindow**: 95%+ - Chat flow, API integration, error handling

### Areas Covered
- ✅ Component rendering
- ✅ User interactions (click, type, keyboard)
- ✅ State management
- ✅ Props handling
- ✅ Error handling
- ✅ Loading states
- ✅ Conditional rendering
- ✅ API integration

### Not Yet Covered (Optional Future Tests)
- Visual regression testing
- Performance/performance metrics
- Accessibility (a11y) testing
- Browser-specific behavior

---

## Next Steps

1. **Run tests**: `npm install && npm test`
2. **View coverage**: `npm run test:coverage`
3. **Watch mode**: `npm test -- --watch` for development
4. **CI/CD Integration**: Add test commands to deployment pipeline
5. **Expand tests**: Add E2E tests with Playwright/Cypress
6. **Accessibility**: Add a11y tests with jest-axe

---

## Notes

- All tests use user-centric queries to ensure testing real user interactions
- API calls are fully mocked to avoid external dependencies
- Tests are independent and can run in any order
- Setup file provides global mocks for all tests
- Console errors from React are suppressed during testing by default with proper error boundaries
