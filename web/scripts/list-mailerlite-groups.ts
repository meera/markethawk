import { getGroups } from '../lib/mailerlite';

async function listGroups() {
  try {
    console.log('Fetching MailerLite groups...\n');

    const groups = await getGroups();

    if (!groups || groups.length === 0) {
      console.log('No groups found.');
      return;
    }

    console.log(`Found ${groups.length} group(s):\n`);

    groups.forEach((group: any) => {
      console.log(`Name: ${group.name}`);
      console.log(`ID: ${group.id}`);
      console.log(`Subscribers: ${group.active_count || 0}`);
      console.log('---');
    });

    console.log('\nAdd these to your .env.local:');
    console.log('\nMAILERLITE_GROUP_NEW_USERS="<group-id-for-new-users>"');
    console.log('MAILERLITE_GROUP_NEWSLETTER="<group-id-for-newsletter>"');

  } catch (error: any) {
    console.error('Error fetching groups:', error.message);
    console.error('\nMake sure MAILERLITE_API_KEY is set in your .env.local file');
  }
}

listGroups();
