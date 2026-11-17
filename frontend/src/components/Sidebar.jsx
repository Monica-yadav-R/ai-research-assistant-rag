
const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '⌂' },
    { id: 'documents', label: 'Documents', icon: '▤' },
    { id: 'chat', label: 'Research Chat', icon: '◉' },
    { id: 'settings', label: 'Settings', icon: '⚙' }
]

function Sidebar({ activePage, setActivePage }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <div className="brand-icon">R</div>
                <div>
                    <h2>Research AI</h2>
                    <span>Research Assistant</span>
                </div>
            </div>

            <p className="sidebar-label">WORKSPACE</p>

            <nav>
                {navigationItems.map((item) => (
                    <button
                        key={item.id}
                        className={`nav-item ${
                            activePage === item.id ? 'active' : ''
                        }`}
                        onClick={() => setActivePage(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        {item.label}
                    </button>
                ))}
            </nav>

            <div className="sidebar-footer">
                <span className="status-dot"></span>
                Local AI backend
            </div>
        </aside>
    )
}

export default Sidebar
