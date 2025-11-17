import { MetadataRoute } from 'next';
import { getCompanies } from '@/lib/db/companies';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://markethawkeye.com';

  // Get all companies for dynamic stock pages
  const companies = await getCompanies({ limit: 10000 });

  // Generate stock page URLs
  const stockUrls = companies.map((company) => ({
    url: `${baseUrl}/stocks/${company.ticker.toLowerCase()}`,
    lastModified: company.updated_at,
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }));

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    {
      url: `${baseUrl}/stocks`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    ...stockUrls,
  ];
}
