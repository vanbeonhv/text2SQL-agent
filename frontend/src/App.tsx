import { Providers } from './app/providers';
import { Navigate, Route, Routes } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { AdminLayout } from './components/admin/AdminLayout';
import { SchemaTablesAdminPage } from './components/admin/SchemaTablesAdminPage';

function App() {
  return (
    <Providers>
      <Routes>
        <Route path="/" element={<MainLayout />} />
        <Route path="/admin" element={<Navigate to="/admin/schema-tables" replace />} />
        <Route element={<AdminLayout />}>
          <Route path="/admin/schema-tables" element={<SchemaTablesAdminPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Providers>
  );
}

export default App;
