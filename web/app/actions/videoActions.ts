'use server';

import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { db } from '@/lib/db';
import { user as userTable, organization as organizationTable } from '@/lib/db/auth-schema';
import { eq } from 'drizzle-orm';
import { getPostHogClient } from '@/lib/posthog-server';

/**
 * Access tier type
 */
export type AccessTier = 'free' | 'pro' | 'team';

/**
 * User access permissions
 */
export interface UserAccess {
  tier: AccessTier;
  canWatchFullVideos: boolean;
  canInteractWithCharts: boolean;
  canDownloadTranscripts: boolean;
  canAccessAPI: boolean;
  isAuthenticated: boolean;
}

/**
 * Get user's access level
 * Returns combined access from personal subscription AND organization membership
 */
export async function getUserAccess(): Promise<UserAccess> {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  // Unauthenticated users: free tier only
  if (!session?.user) {
    return {
      tier: 'free',
      canWatchFullVideos: false,
      canInteractWithCharts: false,
      canDownloadTranscripts: false,
      canAccessAPI: false,
      isAuthenticated: false,
    };
  }

  // TODO: Check personal and organization subscriptions
  // For MVP, all authenticated users have free tier
  const hasProPersonal = false;
  const hasTeamOrg = false;

  // TODO: Implement subscription checking:
  // - Query subscription table or Stripe
  // - Cache subscription tier in organization.metadata
  // - Check org membership and tier

  // User has Pro access if they have EITHER Pro personal OR Team org
  const tier: AccessTier = hasTeamOrg ? 'team' : hasProPersonal ? 'pro' : 'free';

  return {
    tier,
    canWatchFullVideos: hasProPersonal || hasTeamOrg,
    canInteractWithCharts: hasProPersonal || hasTeamOrg,
    canDownloadTranscripts: hasProPersonal || hasTeamOrg,
    canAccessAPI: hasTeamOrg, // Team-only feature
    isAuthenticated: true,
  };
}

/**
 * Check if user can watch full video
 */
export async function canWatchFullVideo(videoId: string) {
  const access = await getUserAccess();

  return {
    canWatch: access.canWatchFullVideos,
    tier: access.tier,
    isAuthenticated: access.isAuthenticated,
  };
}

/**
 * Check if user can interact with charts
 */
export async function canInteractWithCharts() {
  const access = await getUserAccess();

  return {
    canInteract: access.canInteractWithCharts,
    tier: access.tier,
  };
}

/**
 * Check if user can download transcript
 */
export async function canDownloadTranscript(videoId: string) {
  const access = await getUserAccess();

  return {
    canDownload: access.canDownloadTranscripts,
    tier: access.tier,
  };
}

/**
 * Track video view (analytics)
 */
export async function trackVideoView(videoId: string, data: {
  durationWatched?: number;
  progressPercent?: number;
  source?: string;
}) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  try {
    // Track in PostHog
    const posthog = getPostHogClient();
    const distinctId = session?.user?.email || session?.user?.id || 'anonymous';

    posthog.capture({
      distinctId,
      event: 'video_played',
      properties: {
        video_id: videoId,
        duration_watched: data.durationWatched,
        progress_percent: data.progressPercent,
        source: data.source,
        is_authenticated: !!session?.user,
      },
    });
    await posthog.shutdown();

    // TODO: Insert into videoViews table
    // For now, just log
    console.log('Video view tracked:', {
      videoId,
      userId: session?.user?.id || 'anonymous',
      ...data,
    });

    return { success: true };
  } catch (error) {
    console.error('Failed to track video view:', error);
    return {
      error: 'Failed to track view',
      details: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Track video engagement event (paywall hit, chart interaction, etc.)
 */
export async function trackEngagement(videoId: string, eventType: string, data: Record<string, any>) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  try {
    // TODO: Insert into videoEngagement table
    console.log('Engagement tracked:', {
      videoId,
      userId: session?.user?.id || 'anonymous',
      eventType,
      ...data,
    });

    return { success: true };
  } catch (error) {
    console.error('Failed to track engagement:', error);
    return {
      error: 'Failed to track engagement',
      details: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Track paywall hit (for analytics)
 */
export async function trackPaywallHit(videoId: string, progressPercent: number) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  // Track in PostHog - critical conversion funnel event
  const posthog = getPostHogClient();
  const distinctId = session?.user?.email || session?.user?.id || 'anonymous';

  posthog.capture({
    distinctId,
    event: 'paywall_hit',
    properties: {
      video_id: videoId,
      progress_percent: progressPercent,
      is_authenticated: !!session?.user,
      user_tier: session?.user ? 'free' : 'anonymous', // TODO: Get actual tier from subscription
    },
  });
  await posthog.shutdown();

  return trackEngagement(videoId, 'paywall_hit', { progressPercent });
}

/**
 * Track chart interaction
 */
export async function trackChartInteraction(videoId: string, chartType: string) {
  return trackEngagement(videoId, 'chart_interact', { chartType });
}

/**
 * Track download attempt
 */
export async function trackDownloadAttempt(videoId: string, fileType: string) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  // Track in PostHog
  const posthog = getPostHogClient();
  const distinctId = session?.user?.email || session?.user?.id || 'anonymous';

  posthog.capture({
    distinctId,
    event: 'transcript_downloaded',
    properties: {
      video_id: videoId,
      file_type: fileType,
      is_authenticated: !!session?.user,
    },
  });
  await posthog.shutdown();

  return trackEngagement(videoId, 'download_attempt', { fileType });
}
