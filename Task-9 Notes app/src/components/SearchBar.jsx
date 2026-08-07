import React from 'react'

export default function SearchBar({ search, category, onSearchChange, onCategoryChange }) {
  return (
    <div className="searchbar">
      <input
        placeholder="Search by title..."
        value={search}
        onChange={e => onSearchChange(e.target.value)}
      />

      <select value={category} onChange={e => onCategoryChange(e.target.value)}>
        <option>All</option>
        <option>Work</option>
        <option>Personal</option>
        <option>Study</option>
        <option>Other</option>
      </select>
    </div>
  )
}
