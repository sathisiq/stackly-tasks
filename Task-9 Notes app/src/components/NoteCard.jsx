import React from 'react'

export default function NoteCard({ note, onDelete }) {
  return (
    <div className="card">
      <div className="badge">{note.category}</div>
      <h3>{note.title}</h3>
      <p>{note.content}</p>
      <div className="actions">
        <button className="btn" onClick={() => onDelete(note.id)}>Delete</button>
      </div>
    </div>
  )
}
