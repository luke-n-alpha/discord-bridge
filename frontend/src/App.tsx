import { useState } from "react";
import { Button } from "@/components/ui/button";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="flex h-screen bg-background text-foreground font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card p-4 flex flex-col">
        <div className="mb-8 flex items-center gap-2 px-2">
          <div className="h-6 w-6 rounded bg-primary" />
          <span className="text-lg font-bold">Discord Bridge</span>
        </div>

        <nav className="space-y-1 flex-1">
          {["Dashboard", "Settings", "Logs"].map((item) => (
            <Button
              key={item}
              variant={activeTab === item.toLowerCase() ? "secondary" : "ghost"}
              className="w-full justify-start"
              onClick={() => setActiveTab(item.toLowerCase())}
            >
              {item}
            </Button>
          ))}
        </nav>

        <div className="mt-auto pt-4 border-t border-border">
          <div className="text-xs text-muted-foreground px-2">
            v0.1.0 (Tauri)
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-background p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight capitalize">{activeTab}</h1>
          <p className="text-muted-foreground mt-2">
            Welcome to your Discord Summarizer control center.
          </p>
        </header>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {/* Example Cards */}
          <div className="rounded-xl border border-border bg-card text-card-foreground shadow-sm p-6">
            <h3 className="font-semibold leading-none tracking-tight">Total Summaries</h3>
            <div className="mt-4 text-2xl font-bold">1,234</div>
            <p className="text-xs text-muted-foreground mt-1">+20.1% from last month</p>
          </div>
          <div className="rounded-xl border border-border bg-card text-card-foreground shadow-sm p-6">
            <h3 className="font-semibold leading-none tracking-tight">Active Channels</h3>
            <div className="mt-4 text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground mt-1">Updates every hour</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
