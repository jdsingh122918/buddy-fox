import React from 'react';
import { ThemeToggle } from '@/components/ui/theme-toggle';

export const Header: React.FC = () => {
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🦊</span>
            <div>
              <h1 className="text-2xl font-bold">Buddy Fox</h1>
              <p className="text-sm text-muted-foreground">AI Web Browsing Agent</p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};
