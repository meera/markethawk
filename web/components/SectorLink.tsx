'use client';

import Link from 'next/link';
import posthog from 'posthog-js';

interface SectorLinkProps {
  sector: string;
  count: number;
}

export function SectorLink({ sector, count }: SectorLinkProps) {
  const handleClick = () => {
    posthog.capture('sector_filtered', {
      sector: sector,
    });
  };

  return (
    <Link
      href={`/?sector=${encodeURIComponent(sector)}`}
      onClick={handleClick}
      className="px-4 py-2 bg-background-muted/40 border border-border rounded-lg hover:bg-primary/10 hover:border-primary transition-all text-text-secondary hover:text-primary text-sm"
    >
      {sector} <span className="text-text-tertiary">({count})</span>
    </Link>
  );
}
