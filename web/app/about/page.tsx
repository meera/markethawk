'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Logo } from '@/components/Logo';

export default function HomePage() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  async function handleSubscribe(e: React.FormEvent) {
    e.preventDefault();
    setStatus('loading');

    try {
      const res = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email}),
      });

      if (res.ok) {
        setStatus('success');
        setEmail('');
      } else {
        setStatus('error');
      }
    } catch (error) {
      setStatus('error');
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background-elevated to-background">
      {/* Header */}
      <header className="border-b border-border backdrop-blur-sm bg-background/80 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Logo />

            <nav className="flex items-center space-x-6">
              <Link href="/" className="text-text-tertiary hover:text-primary transition-colors text-sm">
                Companies
              </Link>
              <Link href="/about" className="text-primary font-medium transition-colors text-sm">
                About
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="text-center space-y-8">
          <div className="inline-block px-4 py-2 bg-gradient-to-r from-primary/10 to-accent/10 border border-border-accent rounded-full shadow-lg shadow-accent/10">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent text-sm font-medium">See What Transcripts Can't Show ⚡</span>
          </div>

          <h2 className="text-5xl md:text-6xl lg:text-7xl font-bold text-text-primary leading-tight">
            Don't read boring transcripts.
            <br />
            <span className="bg-gradient-to-r from-primary to-primary-light bg-clip-text text-transparent">
              Hear the actual call.
            </span>
          </h2>

          <p className="text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
            Spot discrepancies between what executives say and what the data shows. Catch the hesitation in their voices. Hear the confidence—or lack of it—that words alone can't convey.
          </p>
        </div>
      </section>

      {/* Vision Section */}
      <section id="vision" className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="relative bg-background-muted/50 border border-border backdrop-blur-sm rounded-2xl p-8 md:p-12 overflow-hidden">
          <div className="absolute top-4 right-4 w-3 h-3 bg-accent rounded-full shadow-lg shadow-accent/50 animate-pulse"></div>
          <h3 className="text-3xl font-bold text-text-primary mb-6">Our Vision</h3>

          <div className="space-y-6 text-text-tertiary text-lg leading-relaxed">
            <p>
              <strong className="text-primary">Transcripts strip away what matters most.</strong> The pause. The hesitation. The tone that reveals everything.
            </p>

            <p>
              When a CFO hesitates before answering margin questions, you need to hear it. When revenue numbers don't match their confident tone, that's your signal. When management dodges questions about competition, the silence speaks volumes.
            </p>

            <p>
              With Markey HawkEye, you can:
            </p>

            <ul className="space-y-3 ml-6">
              <li className="flex items-start">
                <span className="text-primary mr-3">•</span>
                <span><strong className="text-text-primary">Hear what executives really mean</strong> - Tone, hesitation, and confidence reveal more than words</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-3">•</span>
                <span><strong className="text-text-primary">Spot discrepancies instantly</strong> - See when the numbers don't match the narrative</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-3">•</span>
                <span><strong className="text-text-primary">Understand market challenges faster</strong> - Visual context makes complex issues clear</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-3">•</span>
                <span><strong className="text-text-primary">Make better investment decisions</strong> - Original audio + synchronized data = complete picture</span>
              </li>
            </ul>

            <p className="pt-4 border-t border-border">
              We don't summarize or paraphrase. You get the <strong className="text-primary">authentic voices of executives</strong> paired with the data that matters. No AI voice, no lost context, no missed signals.
            </p>
          </div>
        </div>
      </section>

      {/* Search Companies */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-background-muted/40 border border-border rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-text-primary mb-4">Find Your Company</h3>
          <p className="text-text-secondary mb-6">Search 7,600+ companies by name or ticker</p>
          <form action="/stocks" method="get" className="max-w-2xl mx-auto">
            <div className="flex gap-3">
              <input
                type="text"
                name="search"
                placeholder="Search AAPL, Apple, Microsoft..."
                className="flex-1 px-6 py-4 rounded-lg bg-background border border-border text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary text-lg"
              />
              <button
                type="submit"
                className="px-8 py-4 bg-primary hover:bg-primary-dark text-white rounded-lg font-semibold transition-all shadow-lg shadow-primary/20"
              >
                Search
              </button>
            </div>
          </form>
          <p className="text-text-tertiary text-sm mt-4">
            Or{' '}
            <Link href="/stocks" className="text-primary hover:text-primary-light underline">
              browse all 7,600+ companies
            </Link>
          </p>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h3 className="text-3xl font-bold text-text-primary mb-12 text-center">Why You'll Never Miss a Signal Again</h3>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="relative group bg-background-muted/40 border border-border rounded-xl p-6 hover:bg-background-muted/60 hover:border-border-accent hover:shadow-lg hover:shadow-accent/10 transition-all">
            <div className="absolute -top-3 -right-3 w-8 h-8 bg-gradient-to-br from-accent to-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-accent/30 font-bold text-white text-sm">1</div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <span className="text-3xl">🎙️</span>
            </div>
            <h4 className="text-xl font-semibold text-primary group-hover:text-primary-light transition-colors mb-3">Catch Every Nuance</h4>
            <p className="text-text-tertiary">
              Hear the actual voices. A CEO's pause. A CFO's hesitation. The confidence—or lack of it—that transcripts miss. Authentic audio reveals what words alone can't.
            </p>
          </div>

          <div className="relative group bg-background-muted/40 border border-border rounded-xl p-6 hover:bg-background-muted/60 hover:border-border-accent hover:shadow-lg hover:shadow-accent/10 transition-all">
            <div className="absolute -top-3 -right-3 w-8 h-8 bg-gradient-to-br from-accent to-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-accent/30 font-bold text-white text-sm">2</div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <span className="text-3xl">📊</span>
            </div>
            <h4 className="text-xl font-semibold text-primary group-hover:text-primary-light transition-colors mb-3">See the Full Picture</h4>
            <p className="text-text-tertiary">
              Charts appear exactly when metrics are mentioned. Spot when the narrative doesn't match the numbers. Connect dots faster with synchronized visual context.
            </p>
          </div>

          <div className="relative group bg-background-muted/40 border border-border rounded-xl p-6 hover:bg-background-muted/60 hover:border-border-accent hover:shadow-lg hover:shadow-accent/10 transition-all">
            <div className="absolute -top-3 -right-3 w-8 h-8 bg-gradient-to-br from-accent to-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-accent/30 font-bold text-white text-sm">3</div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <span className="text-3xl">🎬</span>
            </div>
            <h4 className="text-xl font-semibold text-primary group-hover:text-primary-light transition-colors mb-3">Stay Ahead of the Market</h4>
            <p className="text-text-tertiary">
              Get insights within hours of earnings releases. While others scramble through transcripts, you're already analyzing tone, data, and market implications.
            </p>
          </div>
        </div>
      </section>

      {/* Newsletter Subscription */}
      <section id="subscribe" className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-primary to-primary-dark rounded-2xl p-8 md:p-12 text-center shadow-2xl shadow-primary/20">
          <h3 className="text-3xl font-bold text-white mb-4">Don't Miss the Next Big Signal</h3>
          <p className="text-white/90 mb-8 text-lg">
            Get early access to insights that move markets. Be the first to catch discrepancies, hear executive tone, and spot opportunities before the crowd.
          </p>

          <form onSubmit={handleSubscribe} className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="flex-1 px-6 py-4 rounded-lg bg-white text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-accent text-lg"
                disabled={status === 'loading' || status === 'success'}
              />
              <button
                type="submit"
                disabled={status === 'loading' || status === 'success'}
                className="px-8 py-4 bg-background hover:bg-background-hover hover:ring-2 hover:ring-accent/50 text-white rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed text-lg whitespace-nowrap shadow-lg"
              >
                {status === 'loading' ? 'Subscribing...' : status === 'success' ? 'Subscribed!' : 'Subscribe'}
              </button>
            </div>

            {status === 'success' && (
              <p className="text-white font-medium">
                Thank you for subscribing!
              </p>
            )}

            {status === 'error' && (
              <p className="text-red-200">
                Something went wrong. Please try again.
              </p>
            )}
          </form>

          <p className="text-white/80 text-sm mt-6">
            Join investors who spot what others miss.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border mt-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex items-center space-x-3">
              <div className="relative w-8 h-8 bg-gradient-to-br from-primary to-primary-dark rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">M</span>
                <span className="absolute -top-1 -right-1 w-1.5 h-1.5 bg-accent rounded-full shadow-sm shadow-accent/50"></span>
              </div>
              <span className="text-text-tertiary text-sm">
                © 2024 Markey HawkEye. Transform earnings calls into visual insights.
              </span>
            </div>

            <div className="flex items-center space-x-6 text-sm">
              <Link href="mailto:thehawkeyemarket@gmail.com" className="text-text-tertiary hover:text-accent transition-colors">
                Contact
              </Link>
              <Link href="/privacy" className="text-text-tertiary hover:text-accent transition-colors">
                Privacy
              </Link>
              <Link href="/terms" className="text-text-tertiary hover:text-accent transition-colors">
                Terms
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
