import React, { useEffect, useState } from 'react';
import StatusCard from './StatusCard';
import { fetchStatusData } from '../utils/driveUtils';
import styles from './Dashboard.module.css';

interface StatusData {
  progress: number;
  total: number;
  timestamp: number;
  tier: number;
  objname: string;
}

const REFRESH_INTERVAL = 100000; // 10 seconds

export default function Dashboard() {
  const [statusData, setStatusData] = useState<Record<string, StatusData>>({});
  const [spcFolders, setSpcFolders] = useState<{id: string, name: string}[]>([]);

  const fetchSpcFolders = async () => {
    try {
      const response = await fetch('/api/status/folders');
      const folders = await response.json();
      setSpcFolders(folders);
    } catch (error) {
      console.error('Error fetching SPC folders:', error);
    }
  };

  const updateStatus = async () => {
    try {
      const newStatusData: Record<string, StatusData> = {};
      
      for (const folder of spcFolders) {
        const data = await fetchStatusData(`${folder.id}`);
        newStatusData[folder.name] = data;
      }

      setStatusData(newStatusData);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  useEffect(() => {
    fetchSpcFolders();
  }, []);

  useEffect(() => {
    if (spcFolders.length > 0) {
      updateStatus();

      const interval = setInterval(updateStatus, REFRESH_INTERVAL);

      return () => clearInterval(interval);
    }
  }, [spcFolders]);

  return (
    <div className={styles.dashboard}>
      <h1>Status Dashboard</h1>
      <div className={styles.cardGrid}>
        {Object.entries(statusData).map(([spcId, data]) => (
          <StatusCard 
            key={spcId}
            spcId={spcId}
            data={data}
          />
        ))}
      </div>
    </div>
  );
} 