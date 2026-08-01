import styles from "./Card.module.css";

export default function Card({
  padded = true,
  interactive = false,
  className = "",
  as: Component = "div",
  ...props
}) {
  const classes = [
    styles.card,
    padded ? styles.padded : "",
    interactive ? styles.interactive : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <Component className={classes} {...props} />;
}
