interface StatusData {
  progress: number;
  total: number;
  timestamp: number;
  tier: number;
  objname: string;
}

export async function fetchStatusData(fileid: string): Promise<StatusData> {
  try {
    // Modify API path
    const response = await fetch(`/api/status/file?fileid=${encodeURIComponent(fileid)}`);
    const text = await response.text();
    
    console.log(text)

    // Parse status.txt content
    const [progress, timestamp, tier, objname] = text.trim().split(' ');
    const [current, total] = progress.split('/');

    return {
      progress: parseInt(current),
      total: parseInt(total),
      timestamp: parseInt(timestamp),
      tier: parseInt(tier),
      objname: objname
    };
  } catch (error) {
    console.error(`Error fetching ${fileid}:`, error);
    throw error;
  }
} 