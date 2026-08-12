const statusClass = status => `badge ${status.toLowerCase().replaceAll(' ', '-')}`
export default function ApplicationCard({ application }) {
  return <article className="application-card"><div><strong>{application.company}</strong><p>{application.role} · {application.location || 'Location not specified'}</p></div><span className={statusClass(application.status)}>{application.status}</span><time>Applied {application.applied_on}</time></article>
}
