# ADMIN-DASHBOARD.md

Admin dashboard for monitoring MarketHawk performance, videos, and revenue.

---

## Overview

The admin dashboard is the **primary monitoring tool** (NOT email) for tracking:
- Video performance (views, watch time, CTR)
- Click-through correlation (YouTube → Website)
- Revenue (YouTube ads + subscriptions)
- User engagement and conversions

**Design Principles:**
- **Mobile-first:** Optimized for phone viewing
- **One-glance:** All key metrics visible immediately
- **Real-time:** Poll every 30 seconds
- **Actionable:** Quick actions (hide video, edit metadata, re-upload)

---

## URL & Access

**URL:** `markethawkeye.com/admin`

**Authentication:**
- Require admin role (separate from regular users)
- Two-factor authentication (2FA)
- IP whitelist (optional, for extra security)

---

## Dashboard Layout

### Top Section (Above the Fold)

**Key Metrics Cards:**

```tsx
// app/admin/page.tsx

export default async function AdminDashboard() {
  const stats = await fetchAdminStats();

  return (
    <div className="p-6 space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Views (24h)"
          value={stats.totalViews}
          change={stats.viewsChange}
          icon={<EyeIcon />}
        />
        <StatsCard
          title="Watch Time (hours)"
          value={stats.watchHours}
          change={stats.watchHoursChange}
          icon={<ClockIcon />}
        />
        <StatsCard
          title="New Subscribers"
          value={stats.newSubscribers}
          change={stats.subscribersChange}
          icon={<UsersIcon />}
        />
        <StatsCard
          title="Revenue (30d)"
          value={`$${stats.revenue30d}`}
          change={stats.revenueChange}
          icon={<DollarIcon />}
        />
      </div>

      {/* Top Videos (24h) */}
      <TopVideosTable videos={stats.topVideos} />

      {/* Click-Through Correlation */}
      <ClickThroughChart data={stats.clickThroughs} />

      {/* Revenue Breakdown */}
      <RevenueChart data={stats.revenueBreakdown} />
    </div>
  );
}
```

---

## Key Metrics to Display

### 1. Top Videos (24h)

**Table Columns:**
- Video title (with thumbnail)
- View count (last 24h)
- Change % (vs. previous 24h)
- Click-through count (YouTube → Website)
- CTR (click-through rate)
- Quick actions (edit, hide, re-upload)

**Component:**
```tsx
// components/admin/TopVideosTable.tsx

export function TopVideosTable({videos}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-bold mb-4">Top Videos (24h)</h2>

      <table className="w-full">
        <thead>
          <tr className="text-left text-sm text-gray-500">
            <th className="pb-3">Video</th>
            <th className="pb-3">Views</th>
            <th className="pb-3">Change</th>
            <th className="pb-3">Click-Throughs</th>
            <th className="pb-3">CTR</th>
            <th className="pb-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {videos.map(video => (
            <tr key={video.id} className="border-t">
              <td className="py-3">
                <div className="flex items-center gap-3">
                  <img src={video.thumbnail} className="w-16 h-9 rounded" />
                  <div>
                    <div className="font-medium">{video.title}</div>
                    <div className="text-sm text-gray-500">
                      {video.ticker} • {video.quarter}
                    </div>
                  </div>
                </div>
              </td>
              <td className="py-3 font-semibold">
                {video.views.toLocaleString()}
              </td>
              <td className="py-3">
                <ChangeIndicator value={video.viewsChange} />
              </td>
              <td className="py-3">
                {video.clickThroughs.toLocaleString()}
              </td>
              <td className="py-3">
                {video.ctr.toFixed(2)}%
              </td>
              <td className="py-3">
                <VideoActions videoId={video.id} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ChangeIndicator({value}) {
  const isPositive = value >= 0;
  const color = isPositive ? 'text-green-600' : 'text-red-600';

  return (
    <span className={`${color} font-medium`}>
      {isPositive ? '↑' : '↓'} {Math.abs(value)}%
    </span>
  );
}
```

---

### 2. Click-Through Correlation

**Chart showing:**
- YouTube video views
- Website clicks from video
- Conversion rate (clicks / views)

**Component:**
```tsx
// components/admin/ClickThroughChart.tsx

'use client';

import {Line} from 'react-chartjs-2';

export function ClickThroughChart({data}) {
  const chartData = {
    labels: data.map(d => d.date),
    datasets: [
      {
        label: 'YouTube Views',
        data: data.map(d => d.views),
        borderColor: '#FF0000',
        backgroundColor: 'rgba(255, 0, 0, 0.1)',
      },
      {
        label: 'Website Clicks',
        data: data.map(d => d.clicks),
        borderColor: '#0066FF',
        backgroundColor: 'rgba(0, 102, 255, 0.1)',
      },
    ],
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-bold mb-4">Click-Through Correlation</h2>
      <Line data={chartData} options={chartOptions} />

      <div className="mt-4 text-sm text-gray-600">
        Average CTR: {(data.reduce((sum, d) => sum + d.ctr, 0) / data.length).toFixed(2)}%
      </div>
    </div>
  );
}
```

---

### 3. Revenue Breakdown

**Show:**
- YouTube ad revenue (daily)
- Subscription revenue (MRR)
- Total 30-day revenue
- Projected monthly revenue

**Component:**
```tsx
// components/admin/RevenueChart.tsx

export function RevenueChart({data}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-bold mb-4">Revenue (30 days)</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <RevenueCard
          title="YouTube Ads"
          value={data.youtubeAds}
          daily={data.youtubeAdsDaily}
          color="bg-red-500"
        />
        <RevenueCard
          title="Subscriptions (MRR)"
          value={data.subscriptions}
          daily={data.subscriptionsDaily}
          color="bg-blue-500"
        />
        <RevenueCard
          title="Total Revenue"
          value={data.total}
          daily={data.totalDaily}
          color="bg-green-500"
        />
      </div>

      <Bar data={chartData} options={chartOptions} />
    </div>
  );
}

function RevenueCard({title, value, daily, color}) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className={`w-2 h-2 rounded-full ${color} mb-2`} />
      <div className="text-sm text-gray-600">{title}</div>
      <div className="text-2xl font-bold">${value.toLocaleString()}</div>
      <div className="text-xs text-gray-500">
        ${daily.toFixed(2)}/day
      </div>
    </div>
  );
}
```

---

### 4. Today's Performance

**Metrics:**
- Total views (today)
- Watch time (hours)
- New subscribers
- Website visits (from YouTube)
- Conversions (free → paid)

**Component:**
```tsx
// components/admin/TodayStats.tsx

export function TodayStats({stats}) {
  return (
    <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6 text-white">
      <h2 className="text-lg font-bold mb-4">Today's Performance</h2>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatItem label="Views" value={stats.views} />
        <StatItem label="Watch Hours" value={stats.watchHours} />
        <StatItem label="New Subs" value={stats.newSubscribers} />
        <StatItem label="Website Visits" value={stats.websiteVisits} />
        <StatItem label="Conversions" value={stats.conversions} />
      </div>
    </div>
  );
}

function StatItem({label, value}) {
  return (
    <div>
      <div className="text-sm opacity-80">{label}</div>
      <div className="text-2xl font-bold">{value.toLocaleString()}</div>
    </div>
  );
}
```

---

## Real-Time Updates

### Polling Strategy

```tsx
// app/admin/page.tsx

'use client';

import {useEffect, useState} from 'react';

export function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Initial fetch
    fetchStats();

    // Poll every 30 seconds
    const interval = setInterval(fetchStats, 30000);

    return () => clearInterval(interval);
  }, []);

  async function fetchStats() {
    const res = await fetch('/api/admin/stats');
    const data = await res.json();
    setStats(data);
  }

  if (!stats) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      <StatsCards stats={stats} />
      <TopVideosTable videos={stats.topVideos} />
      {/* ... more components */}
    </div>
  );
}
```

---

## API Endpoint

### GET /api/admin/stats

```typescript
// app/api/admin/stats/route.ts

import {auth} from '@/lib/auth';

export async function GET(req: Request) {
  const session = await auth.getSession();

  // Check admin role
  if (!session || session.user.role !== 'admin') {
    return Response.json({error: 'Unauthorized'}, {status: 401});
  }

  // Fetch stats from database
  const stats = await fetchAdminStats();

  return Response.json(stats);
}

async function fetchAdminStats() {
  const [
    topVideos,
    clickThroughs,
    todayStats,
    revenue,
  ] = await Promise.all([
    fetchTopVideos(),
    fetchClickThroughs(),
    fetchTodayStats(),
    fetchRevenue(),
  ]);

  return {
    topVideos,
    clickThroughs,
    todayStats: {
      totalViews: todayStats.views,
      viewsChange: calculateChange(todayStats.views, yesterdayStats.views),
      watchHours: todayStats.watchHours,
      watchHoursChange: calculateChange(todayStats.watchHours, yesterdayStats.watchHours),
      newSubscribers: todayStats.subscribers,
      subscribersChange: calculateChange(todayStats.subscribers, yesterdayStats.subscribers),
      websiteVisits: todayStats.websiteVisits,
      conversions: todayStats.conversions,
    },
    revenue: {
      youtubeAds: revenue.youtubeAds,
      youtubeAdsDaily: revenue.youtubeAds / 30,
      subscriptions: revenue.subscriptions,
      subscriptionsDaily: revenue.subscriptions / 30,
      total: revenue.total,
      totalDaily: revenue.total / 30,
    },
  };
}
```

---

## Quick Actions

### Video Management Actions

```tsx
// components/admin/VideoActions.tsx

export function VideoActions({videoId}) {
  return (
    <div className="flex gap-2">
      <button
        onClick={() => editVideo(videoId)}
        className="text-blue-600 hover:underline"
      >
        Edit
      </button>
      <button
        onClick={() => hideVideo(videoId)}
        className="text-gray-600 hover:underline"
      >
        Hide
      </button>
      <button
        onClick={() => reUpload(videoId)}
        className="text-orange-600 hover:underline"
      >
        Re-upload
      </button>
      <button
        onClick={() => deleteVideo(videoId)}
        className="text-red-600 hover:underline"
      >
        Delete
      </button>
    </div>
  );
}

async function editVideo(videoId: string) {
  window.location.href = `/admin/videos/${videoId}/edit`;
}

async function hideVideo(videoId: string) {
  if (!confirm('Hide this video? It will no longer appear on the site.')) return;

  await fetch(`/api/admin/videos/${videoId}`, {
    method: 'PATCH',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({status: 'hidden'}),
  });

  window.location.reload();
}

async function reUpload(videoId: string) {
  if (!confirm('Re-upload this video to YouTube? This will create a new video.')) return;

  await fetch(`/api/admin/videos/${videoId}/reupload`, {
    method: 'POST',
  });

  alert('Video queued for re-upload. This may take 10-15 minutes.');
}

async function deleteVideo(videoId: string) {
  if (!confirm('Delete this video PERMANENTLY? This cannot be undone.')) return;

  await fetch(`/api/admin/videos/${videoId}`, {
    method: 'DELETE',
  });

  window.location.reload();
}
```

---

## Mobile Responsiveness

### Mobile-First Design

```tsx
// Tailwind classes for mobile optimization

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Cards stack vertically on mobile, grid on desktop */}
</div>

<table className="w-full text-sm md:text-base">
  {/* Smaller text on mobile */}
</table>

<div className="overflow-x-auto">
  <table className="min-w-full">
    {/* Horizontal scroll on mobile if needed */}
  </table>
</div>
```

### Touch-Friendly Buttons

```tsx
<button className="px-4 py-3 md:px-6 md:py-4 text-lg">
  {/* Larger touch targets on mobile */}
</button>
```

---

## Performance Tracking

### Track These Events

**User Events:**
- `page_view` (page, referrer)
- `video_play` (video_id, source)
- `video_progress` (video_id, progress %)
- `video_complete` (video_id, watch_time)
- `chart_interact` (video_id, chart_type, action)
- `click_through` (video_id, destination)
- `signup` (source, plan)
- `subscription_created` (plan, amount)

**System Events:**
- `video_rendered` (video_id, duration, errors)
- `video_uploaded` (video_id, youtube_id)
- `analytics_synced` (video_id, views, watch_time)

---

## Alerts & Notifications

### Email Alerts (Optional)

**Send email when:**
- Video views spike (>200% increase in 1 hour)
- Revenue milestone reached ($100, $500, $1000/day)
- Error in video processing
- Subscription cancellation spike (>5 in 1 day)

**Implementation:**
```typescript
// lib/alerts.ts

export async function checkAlerts() {
  const stats = await fetchStats();

  if (stats.viewsChange > 200) {
    await sendEmail({
      to: 'admin@markethawkeye.com',
      subject: 'Video views spiking!',
      body: `Views are up ${stats.viewsChange}% in the last hour.`,
    });
  }

  // ... more alert conditions
}
```

---

## Related Documentation

- **DATABASE-SCHEMA.md** - Tables for tracking views, engagement, revenue
- **USER-EXPERIENCE.md** - Conversion tracking (free → paid)
- **WEB-APP-GUIDE.md** - Real-time data fetching with React
- **SEO-STRATEGY.md** - YouTube analytics integration

---

**Last Updated:** 2025-11-10
