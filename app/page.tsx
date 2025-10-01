export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Ustatop.uz Backend</h1>
          <p className="text-lg text-muted-foreground mb-8">FastAPI backend server for Ustatop.uz platform</p>
          <div className="bg-card p-6 rounded-lg border max-w-2xl mx-auto">
            <h2 className="text-2xl font-semibold mb-4">Backend Status</h2>
            <p className="text-muted-foreground">
              The FastAPI backend is ready to be deployed separately. This Next.js frontend is just a placeholder for
              the deployment structure.
            </p>
            <div className="mt-6 space-y-2">
              <p>
                <strong>API Documentation:</strong> /docs
              </p>
              <p>
                <strong>Backend Files:</strong> Located in /backend directory
              </p>
              <p>
                <strong>Database:</strong> SQLite with Alembic migrations
              </p>
              <p className="mt-4 text-sm text-muted-foreground">
                <strong>Admin Login:</strong> admin@ustatop.uz / admin123
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
