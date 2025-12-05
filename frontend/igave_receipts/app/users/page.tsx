"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const router = useRouter();

  // Fetch users
  const loadUsers = () => {
    fetch("http://127.0.0.1:8000/api/users/")
      .then((res) => res.json())
      .then((data) => setUsers(data));
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // Delete user function
  const deleteUser = async (id: number) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this user?");
    if (!confirmDelete) return;

    const res = await fetch(`http://127.0.0.1:8000/api/users/${id}/delete/`, {
      method: "DELETE",
    });

    if (res.ok) {
      loadUsers(); // refresh list
    } else {
      alert("Failed to delete user.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-10 flex justify-center">

      <div className="w-full max-w-5xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl p-8 text-white">

        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">User Management</h1>

          {/* Back button */}
          <button
            onClick={() => router.push("/dashboard")}
            className="px-4 py-2 bg-white/30 hover:bg-white/40 text-white rounded-lg transition border border-white/20"
          >
            ← Back
          </button>
        </div>

        {/* Table */}
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/20 border-b border-white/30">
              <th className="p-3">ID</th>
              <th className="p-3">Username</th>
              <th className="p-3">Password Hash</th>
              <th className="p-3">Date Joined</th>
              <th className="p-3">Staff</th>
              <th className="p-3 text-center">Actions</th>
            </tr>
          </thead>

          <tbody>
            {users.map((u: any) => (
              <tr key={u.id} className="border-b border-white/10 hover:bg-white/20 transition">
                <td className="p-3">{u.id}</td>
                <td className="p-3">{u.username}</td>
                <td className="p-3 text-xs break-all max-w-xs">{u.password}</td>
                <td className="p-3">
                  {new Date(u.date_joined).toLocaleString()}
                </td>
                <td className="p-3">
                  <span
                    className={`px-2 py-1 rounded text-sm ${
                      u.is_staff
                        ? "bg-green-500/40"
                        : "bg-red-500/40"
                    }`}
                  >
                    {u.is_staff ? "Yes" : "No"}
                  </span>
                </td>
                <td className="p-3 text-center">
                  <button
                    onClick={() => deleteUser(u.id)}
                    className="px-3 py-1 bg-red-500/50 hover:bg-red-500/70 text-white rounded-lg text-sm border border-white/20 transition"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>

        </table>
      </div>
    </div>
  );
}