import styles from "./Button.module.css";

export default function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  className = "",
  as: Component = "button",
  ...props
}) {
  const classes = [
    styles.button,
    styles[variant],
    styles[size],
    fullWidth ? styles.full : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <Component className={classes} {...props} />;
}
