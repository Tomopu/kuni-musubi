import { API_BASE_URL } from "@/lib/constants";

export type Party = {
  id: string;
  name: string;
  short_name: string;
};

export async function fetchParties(): Promise<Party[]> {
  const res = await fetch(`${API_BASE_URL}/parties`);
  if (!res.ok) throw new Error(`GET /parties failed: ${res.status}`);
  return res.json();
}

export async function fetchPartyDetail(partyId: string): Promise<unknown> {
  const res = await fetch(`${API_BASE_URL}/parties/${partyId}`);
  if (!res.ok) throw new Error(`GET /parties/${partyId} failed: ${res.status}`);
  return res.json();
}
