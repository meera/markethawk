'use client';

import { useRouter } from 'next/navigation';
import posthog from 'posthog-js';

interface SearchFormProps {
  defaultValue?: string;
}

export function SearchForm({ defaultValue }: SearchFormProps) {
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const search = formData.get('search') as string;

    if (search) {
      // Track search performed
      posthog.capture('search_performed', {
        query: search,
      });

      router.push(`/?search=${encodeURIComponent(search)}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
      <div className="flex gap-3">
        <input
          type="text"
          name="search"
          defaultValue={defaultValue}
          placeholder="Search by company name or ticker (e.g., AAPL, Apple, Microsoft)..."
          className="flex-1 px-6 py-4 rounded-lg bg-background-muted border border-border text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary text-lg"
          autoFocus={!!defaultValue}
        />
        <button
          type="submit"
          className="px-8 py-4 bg-primary hover:bg-primary-dark text-white rounded-lg font-semibold transition-all shadow-lg shadow-primary/20"
        >
          Search
        </button>
      </div>
    </form>
  );
}
