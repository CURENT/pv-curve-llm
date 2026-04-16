import { Link, useLocation } from "react-router-dom";
import { useAppStore } from "../../store/appStore";

export default function Header() {
  const location = useLocation();
  const isDark = useAppStore((s) => s.isDark);
  const toggleDark = useAppStore((s) => s.toggleDark);
  const startNewConversation = useAppStore((s) => s.startNewConversation);
  const connectionStatus = useAppStore((s) => s.connectionStatus);

  const navLinks = [
    { to: "/chat",     label: "Chat"     },
    { to: "/history",  label: "History"  },
    { to: "/settings", label: "Settings" },
  ];

  const dotColor =
    connectionStatus === "connected"    ? "bg-green-400" :
    connectionStatus === "connecting"   ? "bg-yellow-400 animate-pulse" :
                                          "bg-red-400";

  return (
    <header className="h-12 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex-shrink-0">
      {/* Logo */}
      <Link
        to="/chat"
        onClick={startNewConversation}
        className="flex items-center gap-2 font-bold text-gray-900 dark:text-gray-100 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors text-sm"
      >
        <span className="text-indigo-600 text-lg">⚡</span>
        PV Curve
      </Link>

      {/* Nav */}
      <nav className="flex items-center gap-1">
        {navLinks.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
              location.pathname.startsWith(to)
                ? "bg-indigo-50 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-medium"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
            }`}
          >
            {label}
          </Link>
        ))}
      </nav>

      {/* Right side: connection dot + dark toggle */}
      <div className="flex items-center gap-3">
        {/* Connection status dot */}
        <span title={`Backend: ${connectionStatus}`} className={`w-2 h-2 rounded-full ${dotColor}`} />

        {/* Dark mode toggle */}
        <button
          onClick={toggleDark}
          aria-label="Toggle dark mode"
          className="p-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-base"
        >
          {isDark ? "☀️" : "🌙"}
        </button>
      </div>
    </header>
  );
}
