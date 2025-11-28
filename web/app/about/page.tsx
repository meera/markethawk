'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Logo } from '@/components/Logo';
import { Footer } from '@/components/Footer';

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
            There's a strange thing that happens when you listen instead of read. The pauses speak. The hesitations reveal. And the confidence—or the lack of it—becomes impossible to miss. Transcripts flatten everything into words. Audio gives you the geometry of truth.
          </p>
        </div>
      </section>

      {/* Vision Section */}
      <section id="vision" className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="relative bg-background-muted/50 border border-border backdrop-blur-sm rounded-2xl p-8 md:p-12 overflow-hidden">
          <div className="absolute top-4 right-4 w-3 h-3 bg-accent rounded-full shadow-lg shadow-accent/50 animate-pulse motion-reduce:animate-none" aria-hidden="true"></div>
          <h3 className="text-3xl font-bold text-text-primary mb-6">Our Vision</h3>

          <div className="space-y-6 text-text-tertiary text-lg leading-relaxed">
            <p>
              <strong className="text-primary">Here's what you miss when you only read the transcript:</strong> The CFO who takes three seconds too long before answering the margin question. The CEO whose voice lifts when discussing future guidance—or doesn't. The analyst who asks about competition and gets a careful, rehearsed answer that says everything by saying nothing.
            </p>

            <p>
              Transcripts give you the words. Audio gives you the truth between the words.
            </p>

            <p>
              The geometry of an earnings call isn't in what's said—it's in how it's said. Where the energy shifts. Where the confidence cracks. Where the script ends and the real conversation accidentally begins.
            </p>

            <p className="text-text-primary font-medium">
              MarketHawk gives you:
            </p>

            <ul className="space-y-3 ml-6">
              <li className="flex items-start">
                <span className="text-primary mr-3">•</span>
                <span><strong className="text-text-primary">The actual voices.</strong> Not summaries. Not AI interpretations. The executives themselves—with every pause, every inflection, every moment of hesitation intact.</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-3">•</span>
                <span><strong className="text-text-primary">The data, synchronized.</strong> Charts appear exactly when metrics are mentioned. You see the numbers while hearing the spin. The discrepancies become impossible to miss.</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-3">•</span>
                <span><strong className="text-text-primary">The full context.</strong> Thirty minutes reveals what thirty-second clips can't. You get the dynamic, not just the moment.</span>
              </li>
            </ul>

            <p className="pt-4 border-t border-border">
              No AI voice. No paraphrasing. No sanitized summaries. Just the raw earnings call paired with the financial data that matters. Because the truth isn't in the transcript—it's in the tone, the timing, and the things they don't quite say.
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
        <h3 className="text-3xl font-bold text-text-primary mb-12 text-center">How You Actually Use This</h3>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="relative group bg-background-muted/40 border border-border rounded-xl p-6 hover:bg-background-muted/60 hover:border-border-accent hover:shadow-lg hover:shadow-accent/10 transition-all">
            <div className="absolute -top-3 -right-3 w-8 h-8 bg-gradient-to-br from-accent to-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-accent/30 font-bold text-gray-900 text-sm">1</div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4" aria-hidden="true">
              <span className="text-3xl">🎙️</span>
            </div>
            <h4 className="text-xl font-semibold text-primary group-hover:text-primary-light transition-colors mb-3">Listen for the Edges</h4>
            <p className="text-text-tertiary">
              The CEO pauses before the margin question. The CFO's voice tightens when discussing guidance. You hear what the transcript erases—the moments where confidence slips and truth leaks through.
            </p>
          </div>

          <div className="relative group bg-background-muted/40 border border-border rounded-xl p-6 hover:bg-background-muted/60 hover:border-border-accent hover:shadow-lg hover:shadow-accent/10 transition-all">
            <div className="absolute -top-3 -right-3 w-8 h-8 bg-gradient-to-br from-accent to-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-accent/30 font-bold text-gray-900 text-sm">2</div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4" aria-hidden="true">
              <span className="text-3xl">📊</span>
            </div>
            <h4 className="text-xl font-semibold text-primary group-hover:text-primary-light transition-colors mb-3">Watch the Geometry Reveal Itself</h4>
            <p className="text-text-tertiary">
              The chart appears exactly when they mention revenue growth. You see the number. You hear the tone. The gap between what they say and what the data shows becomes impossible to miss.
            </p>
          </div>

          <div className="relative group bg-background-muted/40 border border-border rounded-xl p-6 hover:bg-background-muted/60 hover:border-border-accent hover:shadow-lg hover:shadow-accent/10 transition-all">
            <div className="absolute -top-3 -right-3 w-8 h-8 bg-gradient-to-br from-accent to-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-accent/30 font-bold text-gray-900 text-sm">3</div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4" aria-hidden="true">
              <span className="text-3xl">⚡</span>
            </div>
            <h4 className="text-xl font-semibold text-primary group-hover:text-primary-light transition-colors mb-3">Act Before the Market Does</h4>
            <p className="text-text-tertiary">
              Within hours of the earnings release, you've already heard the hesitation, spotted the discrepancy, and understood what the market will figure out tomorrow. You're not scrambling. You're ahead.
            </p>
          </div>
        </div>
      </section>

      {/* Newsletter Subscription */}
      <section id="subscribe" className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-primary to-primary-dark rounded-2xl p-8 md:p-12 text-center shadow-2xl shadow-primary/20">
          <h3 className="text-3xl font-bold text-white mb-4">The Signal Is Already There</h3>
          <p className="text-white/90 mb-8 text-lg">
            Most people will read the transcript tomorrow and miss it. You'll hear it today—in the pause, the tone, the moment where the script ends and the truth accidentally slips through.
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

      <Footer />
    </div>
  );
}
