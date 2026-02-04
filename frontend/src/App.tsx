import { MainLayout } from './components/layout/MainLayout';
import { Providers } from './app/providers';

function App() {
  return (
    <Providers>
      <MainLayout />
    </Providers>
  );
}

export default App;
