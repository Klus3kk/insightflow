import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [events, setEvents] = useState<any[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);

  // Fetch the welcome message
  useEffect(() => {
    fetch("http://localhost:5000/")
      .then((response) => response.text())
      .then((data) => {
        setMessage(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setMessage("Failed to connect to the backend.");
        setLoading(false);
      });
  }, []);

  // Fetch logged events
  useEffect(() => {
    fetch("http://localhost:5000/events")
      .then((response) => response.json())
      .then((data) => {
        setEvents(data.results || []);
        setEventsLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching events:", error);
        setEvents([]);
        setEventsLoading(false);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to InsightDrift</h1>
        <p>{loading ? "Connecting to the backend..." : message}</p>
      </header>
      <main className="App-main">
        <section className="features">
          <h2>Core Features</h2>
          <div className="feature-list">
            <div className="feature-card">
              <h3>Analyze User Behavior</h3>
              <p>Gain insights with advanced analytics and tracking tools.</p>
            </div>
            <div className="feature-card">
              <h3>Run A/B Tests</h3>
              <p>Optimize your app's performance with data-driven experiments.</p>
            </div>
            <div className="feature-card">
              <h3>Predictive Insights</h3>
              <p>Leverage machine learning to predict user actions.</p>
            </div>
          </div>
        </section>
        <section className="events">
          <h2>Logged Events</h2>
          {eventsLoading ? (
            <p>Loading events...</p>
          ) : events.length === 0 ? (
            <p>No events logged yet.</p>
          ) : (
            <ul className="events-list">
              {events.map((event) => (
                <li key={event.id} className="event-item">
                  <strong>{event.event_type}</strong> by User {event.user_id} at{" "}
                  {new Date(event.timestamp).toLocaleString()}
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
      <footer className="App-footer">
        <p>InsightDrift © 2025</p>
      </footer>
    </div>
  );
}

export default App;
