import styles from "./AttractionCard.module.css";

export default function AttractionCard({ attraction }) {
  return (
    <li className={styles.item}>
      <p className={styles.category}>{attraction.category}</p>
      <h4 className={styles.name}>{attraction.name}</h4>
      <p className={styles.description}>{attraction.description}</p>
    </li>
  );
}

export { styles as attractionStyles };
