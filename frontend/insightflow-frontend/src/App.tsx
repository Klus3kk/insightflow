import { useEffect, useState } from "react";
import "./App.css";
import { Bar } from "react-chartjs-2";
import Chart from "chart.js/auto"; // Import chart.js for visualization

const API_BASE = "http://localhost:5000"; // Update if needed

function App() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [events, setEvents] = useState<any[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [assignedGroup, setAssignedGroup] = useState<string | null>(null);
  const [abResults, setAbResults] = useState<{ A: number; B: number } | null>(null);

  // Fetch Welcome Message
  useEffect(() => {
    fetch(`${API_BASE}/`)
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

  // Fetch Logged Events
  useEffect(() => {
    fetch(`${API_BASE}/events`)
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

  // Assign user to an A/B test
  const assignUserToTest = async () => {
    const userId = "123"; // Replace with a dynamic user ID later
    try {
      const response = await fetch(`${API_BASE}/assign-user/1/${userId}`, {
        method: "POST",
      });
      const data = await response.json();
      setAssignedGroup(data.message.includes("group A") ? "A" : "B");
    } catch (error) {
      console.error("Error assigning user:", error);
    }
  };

  // Log Click Event for A/B Test
  const logClick = async () => {
    if (!assignedGroup) return;
    const userId = "123"; // Replace with dynamic user ID
    try {
      await fetch(`${API_BASE}/log-ab-test-result`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ test_id: 1, user_id: userId, event_type: "click" }),
      });
      alert("Click logged!");
    } catch (error) {
      console.error("Error logging click:", error);
    }
  };

  // Fetch A/B Test Results
  useEffect(() => {
    fetch(`${API_BASE}/ab-test-results/1`)
      .then((response) => response.json())
      .then((data) => {
        setAbResults({ A: data.group_A_results, B: data.group_B_results });
      })
      .catch((error) => console.error("Error fetching A/B test results:", error));
  }, [assignedGroup]); // Re-fetch when assignedGroup changes

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

        {/* A/B Testing Section */}
        <section className="ab-tests">
          <h2>A/B Testing</h2>
          <button onClick={assignUserToTest}>Join A/B Test</button>
          {assignedGroup && <p>You are in **Group {assignedGroup}**.</p>}

          <h2>Click Tracking</h2>
          <button onClick={logClick}>Click Me!</button>
        </section>

        {/* A/B Test Results */}
        <section className="ab-results">
          <h2>A/B Test Results</h2>
          {abResults ? (
            <Bar
              data={{
                labels: ["Group A", "Group B"],
                datasets: [
                  {
                    label: "Clicks",
                    data: [abResults.A, abResults.B],
                    backgroundColor: ["#4a90e2", "#f76c6c"],
                  },
                ],
              }}
            />
          ) : (
            <p>Loading results...</p>
          )}
        </section>

        {/* Logged Events */}
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
