'use client';

import { useEffect } from 'react';
import Script from 'next/script';
import { useSession } from '@/lib/auth-client';

export function GoogleOneTap() {
  const { data: session } = useSession();

  useEffect(() => {
    // Only show if user is not logged in
    if (session) return;

    // Check if user dismissed One Tap
    const dismissed = localStorage.getItem('google_one_tap_dismissed');
    if (dismissed) return;

    // Initialize Google One Tap
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
        callback: handleCredentialResponse,
        auto_select: true, // Auto-select if user previously signed in
        cancel_on_tap_outside: false, // Don't close on outside click
        context: 'signin',
      });

      // Display the One Tap prompt
      window.google.accounts.id.prompt((notification: any) => {
        if (notification.isNotDisplayed()) {
          console.log('One Tap not displayed:', notification.getNotDisplayedReason());
        }

        if (notification.isSkippedMoment()) {
          console.log('One Tap skipped:', notification.getSkippedReason());
        }

        if (notification.getDismissedReason()) {
          // User dismissed, don't show again this session
          localStorage.setItem('google_one_tap_dismissed', 'true');
        }
      });
    }
  }, [session]);

  async function handleCredentialResponse(response: any) {
    try {
      // Send credential to Better Auth backend
      const res = await fetch('/api/auth/google-one-tap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: response.credential }),
      });

      if (res.ok) {
        // User is now signed in, reload page
        window.location.reload();
      } else {
        console.error('Failed to sign in with Google One Tap');
      }
    } catch (error) {
      console.error('Error signing in with Google One Tap:', error);
    }
  }

  // Don't render if user is already logged in
  if (session) return null;

  return (
    <>
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => console.log('Google One Tap script loaded')}
      />
      <div id="g_id_onload" />
    </>
  );
}

// Extend Window interface for TypeScript
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          prompt: (callback?: (notification: any) => void) => void;
        };
      };
    };
  }
}
