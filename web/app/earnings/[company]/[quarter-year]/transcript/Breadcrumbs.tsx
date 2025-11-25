import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

interface BreadcrumbsProps {
  company: string;
  companyName: string;
  quarter: string;
  year: number;
  quarterYear: string;
}

export function Breadcrumbs({
  company,
  companyName,
  quarter,
  year,
  quarterYear,
}: BreadcrumbsProps) {
  return (
    <nav aria-label="Breadcrumb" className="mb-4">
      <ol className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
        <li>
          <Link href="/" className="hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
            Home
          </Link>
        </li>
        <li>
          <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-600" />
        </li>
        <li>
          <Link href={`/companies/${company}`} className="hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
            {companyName}
          </Link>
        </li>
        <li>
          <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-600" />
        </li>
        <li>
          <Link
            href={`/earnings/${company}/${quarterYear}`}
            className="hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          >
            {quarter} {year} Earnings
          </Link>
        </li>
        <li>
          <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-600" />
        </li>
        <li className="text-gray-900 dark:text-gray-100 font-medium" aria-current="page">
          Transcript
        </li>
      </ol>
    </nav>
  );
}
