import React from 'react';
import styles from './StatusCard.module.css';

interface StatusCardProps {
  spcId: string;
  data: {
    progress: number;
    total: number;
    timestamp: number;
    tier: number;
    objname: string;
  };
}

export default function StatusCard({ spcId, data }: StatusCardProps) {
  const percentage = Math.round((data.progress / data.total) * 100);
  const date = new Date(data.timestamp * 1000).toLocaleString();

  return (
    <div className={styles.card}>
      <h2>{spcId.toUpperCase()}</h2>
      <div className={styles.progressBar}>
        <div 
          className={styles.progress}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className={styles.details}>
        <p>Progress: {data.progress} / {data.total} ({percentage}%)</p>
        <p>Last Update: <span style={{
          color: (Date.now() - data.timestamp * 1000) < 0.7 * 60 * 60 * 1000 ? 'green' : 
                 (Date.now() - data.timestamp * 1000) < 1 * 60 * 60 * 1000 ? 'yellow' : 'inherit'
        }}>{date}</span></p>
        <p>Tier: {data.tier}</p>
        <p>Object: {data.objname}</p>
      </div>
    </div>
  );
} 