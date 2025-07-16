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
    const { fileid } = req.query;
    
    if (!fileid || typeof fileid !== 'string') {
      return res.status(400).json({ error: 'File path is required' });
    }
    
    const authClient = await auth.getClient();
    const drive = google.drive({ version: 'v3', auth: authClient });

    const folder = await drive.files.list({
      q: `'${fileid}' in parents and mimeType='application/vnd.google-apps.folder'`,
      fields: 'files(id)'
    });

    if (!folder.data.files || folder.data.files.length === 0) {
      return res.status(404).json({ error: 'No files found in the specified folder' });
    }

    const file = await drive.files.list({
      q: `name = 'status.txt' and '${folder.data.files[0].id}' in parents`,
      fields: 'files(id, name)',
      spaces: 'drive'
    });

    if (file.data.files.length === 0) {
      throw new Error('Status file not found');
    }

    const statusFile = await drive.files.get({
      fileId: file.data.files[0].id,
      alt: 'media'
    });

    if (!statusFile || !statusFile.data) {
      throw new Error('Status file content not found');
    }

    res.status(200).send(statusFile.data);

  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ error: 'Failed to fetch status' });
  }
} 