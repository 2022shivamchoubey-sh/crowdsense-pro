import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

export function LiveChart({ history }) {
  return (
    <ResponsiveContainer width='100%' height={250}>
      <LineChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray='3 3' stroke='rgba(255,255,255,0.1)' vertical={false} />
        <XAxis dataKey='time' stroke='#94a3b8' tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis stroke='#94a3b8' tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip 
          contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
          itemStyle={{ color: '#fff' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Line type='monotone' dataKey='people' stroke='#ec4899' strokeWidth={3} dot={false} activeDot={{ r: 6, fill: '#ec4899', stroke: '#fff', strokeWidth: 2 }} animationDuration={300} />
        <Line type='monotone' dataKey='vehicles' stroke='#3b82f6' strokeWidth={3} dot={false} activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }} animationDuration={300} />
      </LineChart>
    </ResponsiveContainer>
  );
}
