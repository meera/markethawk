import MailerLite from '@mailerlite/mailerlite-nodejs';

// Initialize MailerLite client
const mailerlite = new MailerLite({
  api_key: process.env.MAILERLITE_API_KEY || '',
});

export interface SubscriberData {
  email: string;
  name?: string;
  fields?: Record<string, string | number>;
}

/**
 * Subscribe an email to MailerLite newsletter group
 * @param data - Subscriber information
 * @param groupId - Optional group ID to add subscriber to
 * @returns Success status
 */
export async function subscribeToNewsletter(
  data: SubscriberData,
  groupId?: string
): Promise<boolean> {
  console.log('[MailerLite] subscribeToNewsletter called with:', { data, groupId });

  if (!process.env.MAILERLITE_API_KEY) {
    console.error('[MailerLite] MAILERLITE_API_KEY is not set');
    throw new Error('MailerLite API key not configured');
  }

  try {
    const params = {
      email: data.email,
      ...(data.name && { name: data.name }),
      ...(data.fields && { fields: data.fields }),
      ...(groupId && { groups: [groupId] }), // Add to group in single API call
    };

    console.log('[MailerLite] API params:', JSON.stringify(params, null, 2));

    const response = await mailerlite.subscribers.createOrUpdate(params);
    console.log('[MailerLite] Subscription successful! Response:', response.data);

    return true;
  } catch (error: any) {
    console.error('[MailerLite] Subscription error:', error.response?.data || error.message);
    console.error('[MailerLite] Full error:', error);
    throw error;
  }
}

/**
 * Send welcome email to new user
 * @param email - User email
 * @param name - User name
 * @returns Success status
 */
export async function sendWelcomeEmail(email: string, name?: string): Promise<boolean> {
  console.log('[MailerLite] sendWelcomeEmail called with:', { email, name });

  if (!process.env.MAILERLITE_API_KEY) {
    console.error('[MailerLite] MAILERLITE_API_KEY is not set');
    throw new Error('MailerLite API key not configured');
  }

  const groupId = process.env.MAILERLITE_GROUP_NEW_USERS;
  console.log('[MailerLite] NEW_USERS group ID from env:', groupId);

  if (!groupId) {
    console.error('[MailerLite] MAILERLITE_GROUP_NEW_USERS is not set');
    throw new Error('Welcome email group not configured');
  }

  try {
    console.log('[MailerLite] Calling subscribeToNewsletter with group:', groupId);

    // Add subscriber to "New Users" group
    // This will trigger the welcome email automation in MailerLite
    await subscribeToNewsletter(
      {
        email,
        name,
        fields: {
          source: 'account_signup',
          signup_date: new Date().toISOString(),
        },
      },
      groupId
    );

    console.log(`[MailerLite] Welcome email triggered successfully for ${email}`);
    return true;
  } catch (error: any) {
    console.error('[MailerLite] Failed to send welcome email:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Add subscriber to a specific group by subscriber ID
 * @param subscriberId - MailerLite subscriber ID
 * @param groupId - MailerLite group ID
 */
export async function addToGroup(subscriberId: string, groupId: string): Promise<boolean> {
  if (!process.env.MAILERLITE_API_KEY) {
    throw new Error('MailerLite API key not configured');
  }

  try {
    // Add to group using the correct API method
    await (mailerlite as any).groups.assignSubscriber(groupId, subscriberId);

    console.log(`Added subscriber ${subscriberId} to group ${groupId}`);
    return true;
  } catch (error: any) {
    console.error('Failed to add subscriber to group:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Get all MailerLite groups (for reference)
 */
export async function getGroups() {
  if (!process.env.MAILERLITE_API_KEY) {
    throw new Error('MailerLite API key not configured');
  }

  try {
    const response = await (mailerlite as any).groups.get({});
    return response.data;
  } catch (error: any) {
    console.error('Failed to fetch groups:', error.response?.data || error.message);
    throw error;
  }
}
