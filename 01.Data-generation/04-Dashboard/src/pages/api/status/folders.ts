import type { NextApiRequest, NextApiResponse } from 'next';
import { GOOGLE_DRIVE_CONFIG } from '@/config/drive';

const { google } = require('googleapis');
const path = require('path');
const fs = require('fs');
const auth = new google.auth.GoogleAuth({
  keyFile: path.join(__dirname, '../../../../../', GOOGLE_DRIVE_CONFIG.JSON_FILE),
  scopes: ['https://www.googleapis.com/auth/drive'],
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {

    const authClient = await auth.getClient();
    const drive = google.drive({ version: 'v3', auth: authClient });

    const res1 = await drive.files.list({
      q: `'${GOOGLE_DRIVE_CONFIG.FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder'`,
      fields: 'files(id, name)',
    });

    // console.log(res1.data)

    const folders = res1.data.files ? res1.data.files
      .filter((file: any) => file.name.toLowerCase().startsWith('spc'))
      .map((file: any) => file) : [];

    res.status(200).json(folders);
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ error: 'Failed to fetch folders' });
  }
} 