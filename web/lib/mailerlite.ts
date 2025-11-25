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
  if (!process.env.MAILERLITE_API_KEY) {
    console.error('MAILERLITE_API_KEY is not set');
    throw new Error('MailerLite API key not configured');
  }

  try {
    const params = {
      email: data.email,
      ...(data.name && { name: data.name }),
      ...(data.fields && { fields: data.fields }),
      status: 'active', // Set to 'unconfirmed' if you want double opt-in
    };

    const response = await mailerlite.subscribers.createOrUpdate(params);
    console.log('MailerLite subscription successful:', response.data);

    // Add to group if specified
    if (groupId && response.data?.id) {
      await addToGroup(response.data.id, groupId);
    }

    return true;
  } catch (error: any) {
    console.error('MailerLite subscription error:', error.response?.data || error.message);
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
  if (!process.env.MAILERLITE_API_KEY) {
    console.error('MAILERLITE_API_KEY is not set');
    throw new Error('MailerLite API key not configured');
  }

  const groupId = process.env.MAILERLITE_GROUP_NEW_USERS;
  if (!groupId) {
    console.error('MAILERLITE_GROUP_NEW_USERS is not set');
    throw new Error('Welcome email group not configured');
  }

  try {
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

    console.log(`Welcome email triggered for ${email}`);
    return true;
  } catch (error: any) {
    console.error('Failed to send welcome email:', error.response?.data || error.message);
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
    // Add to group
    await mailerlite.subscribers.assignToGroup(subscriberId, groupId);

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
    const response = await mailerlite.groups.get();
    return response.data;
  } catch (error: any) {
    console.error('Failed to fetch groups:', error.response?.data || error.message);
    throw error;
  }
}
