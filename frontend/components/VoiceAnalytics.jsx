// import React, { useState, useEffect } from 'react';
// import { FiBarChart2, FiClock, FiCheckCircle, FiXCircle, FiTrendingUp } from 'react-icons/fi';

// const VoiceAnalytics = () => {
//   const [analytics, setAnalytics] = useState(null);
//   const [isLoading, setIsLoading] = useState(true);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     fetchAnalytics();
//     const interval = setInterval(fetchAnalytics, 3000); // Update every 3 seconds
//     return () => clearInterval(interval);
//   }, []);

//   const fetchAnalytics = async () => {
//     try {
//       const response = await fetch('http://127.0.0.1:8000/api/voice/analytics');
//       if (!response.ok) throw new Error('Failed to fetch analytics');
//       const data = await response.json();
//       setAnalytics(data);
//       setError(null);
//     } catch (err) {
//       setError(err.message);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   if (isLoading) {
//     return (
//       <div className="voice-analytics loading">
//         <div className="loading-spinner"></div>
//         <p>Loading voice analytics...</p>
//       </div>
//     );
//   }

//   if (error) {
//     return (
//       <div className="voice-analytics error">
//         <FiXCircle className="error-icon" />
//         <p>Error loading analytics: {error}</p>
//       </div>
//     );
//   }

//   if (!analytics) {
//     return (
//       <div className="voice-analytics">
//         <p>No analytics data available</p>
//       </div>
//     );
//   }

//   return (
//     <div className="voice-analytics">
//       <div className="analytics-header">
//         <FiBarChart2 className="header-icon" />
//         <h3>Voice Command Analytics</h3>
//         <span className="last-update">Live</span>
//       </div>

//       {/* Key Metrics */}
//       <div className="metrics-grid">
//         <div className="metric-card">
//           <div className="metric-icon">
//             <FiTrendingUp />
//           </div>
//           <div className="metric-content">
//             <span className="metric-value">{analytics.total_commands}</span>
//             <span className="metric-label">Total Commands</span>
//           </div>
//         </div>

//         <div className="metric-card success">
//           <div className="metric-icon">
//             <FiCheckCircle />
//           </div>
//           <div className="metric-content">
//             <span className="metric-value">{analytics.success_rate.toFixed(1)}%</span>
//             <span className="metric-label">Success Rate</span>
//           </div>
//         </div>

//         <div className="metric-card">
//           <div className="metric-icon">
//             <FiClock />
//           </div>
//           <div className="metric-content">
//             <span className="metric-value">{analytics.avg_response_time.toFixed(2)}s</span>
//             <span className="metric-label">Avg Response</span>
//           </div>
//         </div>
//       </div>

//       {/* Popular Commands */}
//       <div className="popular-commands">
//         <h4>🎯 Popular Commands</h4>
//         <div className="commands-list">
//           {Object.entries(analytics.popular_commands).map(([command, count]) => (
//             <div key={command} className="command-item">
//               <span className="command-name">{command.replace('_', ' ')}</span>
//               <span className="command-count">{count}</span>
//             </div>
//           ))}
//         </div>
//       </div>

//       {/* Last Command */}
//       {analytics.last_command && (
//         <div className="last-command">
//           <h4>📋 Last Command</h4>
//           <div className="last-command-details">
//             <p><strong>Command:</strong> {analytics.last_command.command?.original_text}</p>
//             <p><strong>Response:</strong> {analytics.last_command.response}</p>
//             <p><strong>Time:</strong> {analytics.last_command.response_time.toFixed(2)}s</p>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default VoiceAnalytics;